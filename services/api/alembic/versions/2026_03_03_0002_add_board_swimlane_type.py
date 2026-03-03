"""add_board_swimlane_type

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-03-03

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: str | None = "c3d4e5f6a7b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add swimlane_type to boards table ('none', 'epic', 'assignee')."""
    op.add_column(
        "boards",
        sa.Column("swimlane_type", sa.String(20), nullable=False, server_default="none"),
    )


def downgrade() -> None:
    """Remove swimlane_type from boards."""
    op.drop_column("boards", "swimlane_type")
