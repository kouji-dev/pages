"""add_page_space_permissions_tables

Revision ID: 8a9b0c1d2e3f
Revises: 7f8e9d0c1b2a
Create Date: 2025-12-18 21:43:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8a9b0c1d2e3f"
down_revision: str | None = "7f8e9d0c1b2a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create page_permissions and space_permissions tables."""
    # Page permissions table
    op.create_table(
        "page_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("page_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("inherited_from_space", sa.Boolean(), nullable=False, server_default="false"),
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
        sa.ForeignKeyConstraint(["page_id"], ["pages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("page_id", "user_id", name="uq_page_permission"),
    )
    op.create_index("ix_page_permissions_page_id", "page_permissions", ["page_id"])
    op.create_index("ix_page_permissions_user_id", "page_permissions", ["user_id"])

    # Space permissions table
    op.create_table(
        "space_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("space_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False),
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
        sa.ForeignKeyConstraint(["space_id"], ["spaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("space_id", "user_id", name="uq_space_permission"),
    )
    op.create_index("ix_space_permissions_space_id", "space_permissions", ["space_id"])
    op.create_index("ix_space_permissions_user_id", "space_permissions", ["user_id"])


def downgrade() -> None:
    """Drop page_permissions and space_permissions tables."""
    op.drop_index("ix_space_permissions_user_id", table_name="space_permissions")
    op.drop_index("ix_space_permissions_space_id", table_name="space_permissions")
    op.drop_table("space_permissions")
    op.drop_index("ix_page_permissions_user_id", table_name="page_permissions")
    op.drop_index("ix_page_permissions_page_id", table_name="page_permissions")
    op.drop_table("page_permissions")
