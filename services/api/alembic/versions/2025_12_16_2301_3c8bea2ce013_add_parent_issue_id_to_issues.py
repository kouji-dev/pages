"""add_parent_issue_id_to_issues

Revision ID: 3c8bea2ce013
Revises: 842e538d2355
Create Date: 2025-12-16 23:01:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3c8bea2ce013"
down_revision: str | None = "842e538d2355"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add parent_issue_id column to issues table."""
    op.add_column(
        "issues",
        sa.Column(
            "parent_issue_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_issues_parent_issue_id",
        "issues",
        "issues",
        ["parent_issue_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_issues_parent_issue_id", "issues", ["parent_issue_id"])


def downgrade() -> None:
    """Remove parent_issue_id column from issues table."""
    op.drop_index("ix_issues_parent_issue_id", table_name="issues")
    op.drop_constraint("fk_issues_parent_issue_id", "issues", type_="foreignkey")
    op.drop_column("issues", "parent_issue_id")
