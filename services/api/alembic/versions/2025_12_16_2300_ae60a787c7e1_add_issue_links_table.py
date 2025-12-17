"""add_issue_links_table

Revision ID: ae60a787c7e1
Revises: 27d8199ceaf3
Create Date: 2025-12-16 23:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ae60a787c7e1"
down_revision: str | None = "27d8199ceaf3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create issue_links table."""
    op.create_table(
        "issue_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_issue_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_issue_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("link_type", sa.String(length=50), nullable=False),
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
        sa.ForeignKeyConstraint(["source_issue_id"], ["issues.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_issue_id"], ["issues.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_issue_links_source_issue_id", "issue_links", ["source_issue_id"])
    op.create_index("ix_issue_links_target_issue_id", "issue_links", ["target_issue_id"])
    op.create_index("ix_issue_links_link_type", "issue_links", ["link_type"])


def downgrade() -> None:
    """Drop issue_links table."""
    op.drop_index("ix_issue_links_link_type", table_name="issue_links")
    op.drop_index("ix_issue_links_target_issue_id", table_name="issue_links")
    op.drop_index("ix_issue_links_source_issue_id", table_name="issue_links")
    op.drop_table("issue_links")
