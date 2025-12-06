"""Add issue_activities table

Revision ID: 0003
Revises: 0002
Create Date: 2024-12-05

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Issue activities table
    op.create_table(
        "issue_activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issue_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("field_name", sa.String(50), nullable=True),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_issue_activities_issue_id", "issue_activities", ["issue_id"])
    op.create_index("ix_issue_activities_user_id", "issue_activities", ["user_id"])
    op.create_index("ix_issue_activities_action", "issue_activities", ["action"])


def downgrade() -> None:
    op.drop_index("ix_issue_activities_action", table_name="issue_activities")
    op.drop_index("ix_issue_activities_user_id", table_name="issue_activities")
    op.drop_index("ix_issue_activities_issue_id", table_name="issue_activities")
    op.drop_table("issue_activities")
