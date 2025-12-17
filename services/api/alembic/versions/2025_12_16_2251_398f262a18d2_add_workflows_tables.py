"""add_workflows_tables

Revision ID: 398f262a18d2
Revises: add_sprints_backlog
Create Date: 2025-12-16 22:51:46.897271

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "398f262a18d2"
down_revision: str | None = "add_sprints_backlog"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create workflows, workflow_statuses, and workflow_transitions tables."""
    # Workflows table
    op.create_table(
        "workflows",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workflows_project_id", "workflows", ["project_id"])
    op.create_index("ix_workflows_is_default", "workflows", ["is_default"])

    # Workflow statuses table
    op.create_table(
        "workflow_statuses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("is_initial", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_final", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["workflow_id"], ["workflows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workflow_statuses_workflow_id", "workflow_statuses", ["workflow_id"])

    # Workflow transitions table
    op.create_table(
        "workflow_transitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_status_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("to_status_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["workflow_id"], ["workflows.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["from_status_id"], ["workflow_statuses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_status_id"], ["workflow_statuses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workflow_transitions_workflow_id", "workflow_transitions", ["workflow_id"])
    op.create_index(
        "ix_workflow_transitions_from_status_id", "workflow_transitions", ["from_status_id"]
    )
    op.create_index(
        "ix_workflow_transitions_to_status_id", "workflow_transitions", ["to_status_id"]
    )


def downgrade() -> None:
    """Drop workflows, workflow_statuses, and workflow_transitions tables."""
    op.drop_index("ix_workflow_transitions_to_status_id", table_name="workflow_transitions")
    op.drop_index("ix_workflow_transitions_from_status_id", table_name="workflow_transitions")
    op.drop_index("ix_workflow_transitions_workflow_id", table_name="workflow_transitions")
    op.drop_table("workflow_transitions")
    op.drop_index("ix_workflow_statuses_workflow_id", table_name="workflow_statuses")
    op.drop_table("workflow_statuses")
    op.drop_index("ix_workflows_is_default", table_name="workflows")
    op.drop_index("ix_workflows_project_id", table_name="workflows")
    op.drop_table("workflows")
