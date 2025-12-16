"""add_sprints_and_backlog_order

Revision ID: add_sprints_backlog
Revises: 46fc6f4041c4
Create Date: 2025-12-16 20:56:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_sprints_backlog"
down_revision: str | None = "46fc6f4041c4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add backlog_order to issues table for backlog prioritization
    op.add_column(
        "issues",
        sa.Column(
            "backlog_order",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_issues_backlog_order",
        "issues",
        ["backlog_order"],
        unique=False,
    )

    # Sprints table
    op.create_table(
        "sprints",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("goal", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="planned"),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sprints_project_id", "sprints", ["project_id"])
    op.create_index("ix_sprints_start_date", "sprints", ["start_date"])
    op.create_index("ix_sprints_end_date", "sprints", ["end_date"])
    op.create_index("ix_sprints_status", "sprints", ["status"])

    # Sprint-Issue junction table
    op.create_table(
        "sprint_issues",
        sa.Column("sprint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issue_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
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
        sa.ForeignKeyConstraint(["sprint_id"], ["sprints.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("sprint_id", "issue_id"),
    )
    op.create_index("ix_sprint_issues_sprint_id", "sprint_issues", ["sprint_id"])
    op.create_index("ix_sprint_issues_issue_id", "sprint_issues", ["issue_id"])


def downgrade() -> None:
    op.drop_index("ix_sprint_issues_issue_id", table_name="sprint_issues")
    op.drop_index("ix_sprint_issues_sprint_id", table_name="sprint_issues")
    op.drop_table("sprint_issues")
    op.drop_index("ix_sprints_status", table_name="sprints")
    op.drop_index("ix_sprints_end_date", table_name="sprints")
    op.drop_index("ix_sprints_start_date", table_name="sprints")
    op.drop_index("ix_sprints_project_id", table_name="sprints")
    op.drop_table("sprints")
    op.drop_index("ix_issues_backlog_order", table_name="issues")
    op.drop_column("issues", "backlog_order")
