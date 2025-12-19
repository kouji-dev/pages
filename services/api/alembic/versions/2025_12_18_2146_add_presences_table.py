"""add_presences_table

Revision ID: 1d2e3f4a5b6c
Revises: 0c1d2e3f4a5b
Create Date: 2025-12-18 21:46:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1d2e3f4a5b6c"
down_revision: str | None = "0c1d2e3f4a5b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create presences table for real-time collaboration."""
    op.create_table(
        "presences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("page_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cursor_position", sa.Text(), nullable=True),
        sa.Column("selection", sa.Text(), nullable=True),
        sa.Column("socket_id", sa.String(length=255), nullable=True),
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
        sa.UniqueConstraint("page_id", "user_id", name="uq_presence"),
    )
    op.create_index("ix_presences_page_id", "presences", ["page_id"])
    op.create_index("ix_presences_user_id", "presences", ["user_id"])
    op.create_index("ix_presences_socket_id", "presences", ["socket_id"])


def downgrade() -> None:
    """Drop presences table."""
    op.drop_index("ix_presences_socket_id", table_name="presences")
    op.drop_index("ix_presences_user_id", table_name="presences")
    op.drop_index("ix_presences_page_id", table_name="presences")
    op.drop_table("presences")
