"""add_updated_at_to_page_versions

Revision ID: 43e25464cdbc
Revises: 1d2e3f4a5b6c
Create Date: 2025-12-30 21:55:09.690663

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "43e25464cdbc"
down_revision: str | None = "1d2e3f4a5b6c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add updated_at column to page_versions table."""
    op.add_column(
        "page_versions",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Remove updated_at column from page_versions table."""
    op.drop_column("page_versions", "updated_at")
