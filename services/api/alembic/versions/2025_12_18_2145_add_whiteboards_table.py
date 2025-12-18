"""add_whiteboards_table

Revision ID: 0c1d2e3f4a5b
Revises: 9b0c1d2e3f4a
Create Date: 2025-12-18 21:45:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0c1d2e3f4a5b"
down_revision: str | None = "9b0c1d2e3f4a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create whiteboards table."""
    op.create_table(
        "whiteboards",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("space_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("data", sa.Text(), nullable=True),  # JSON data (drawings, shapes, text)
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_whiteboards_space_id", "whiteboards", ["space_id"])


def downgrade() -> None:
    """Drop whiteboards table."""
    op.drop_index("ix_whiteboards_space_id", table_name="whiteboards")
    op.drop_table("whiteboards")
