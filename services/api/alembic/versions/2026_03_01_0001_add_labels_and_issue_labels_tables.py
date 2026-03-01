"""add_labels_and_issue_labels_tables

Revision ID: a1b2c3d4e5f6
Revises: f6618c83390b
Create Date: 2026-03-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "f6618c83390b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create labels and issue_labels tables."""
    op.create_table(
        "labels",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("color", sa.String(7), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_label_project_name"),
    )
    op.create_index("ix_labels_project_id", "labels", ["project_id"], unique=False)

    op.create_table(
        "issue_labels",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issue_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("label_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["label_id"], ["labels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("issue_id", "label_id", name="uq_issue_label"),
    )
    op.create_index("ix_issue_labels_issue_id", "issue_labels", ["issue_id"], unique=False)
    op.create_index("ix_issue_labels_label_id", "issue_labels", ["label_id"], unique=False)


def downgrade() -> None:
    """Drop issue_labels and labels tables."""
    op.drop_index("ix_issue_labels_label_id", "issue_labels")
    op.drop_index("ix_issue_labels_issue_id", "issue_labels")
    op.drop_table("issue_labels")
    op.drop_index("ix_labels_project_id", "labels")
    op.drop_table("labels")
