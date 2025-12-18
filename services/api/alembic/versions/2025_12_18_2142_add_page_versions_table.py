"""add_page_versions_table

Revision ID: 7f8e9d0c1b2a
Revises: 1432f294aabb
Create Date: 2025-12-18 21:42:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7f8e9d0c1b2a"
down_revision: str | None = "1432f294aabb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create page_versions table for version history."""
    op.create_table(
        "page_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("page_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["page_id"], ["pages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("page_id", "version_number", name="uq_page_version"),
    )
    op.create_index("ix_page_versions_page_id", "page_versions", ["page_id"])
    op.create_index("ix_page_versions_version_number", "page_versions", ["version_number"])
    op.create_index(
        "ix_page_versions_page_id_version_number",
        "page_versions",
        ["page_id", "version_number"],
    )


def downgrade() -> None:
    """Drop page_versions table."""
    op.drop_index("ix_page_versions_page_id_version_number", table_name="page_versions")
    op.drop_index("ix_page_versions_version_number", table_name="page_versions")
    op.drop_index("ix_page_versions_page_id", table_name="page_versions")
    op.drop_table("page_versions")
