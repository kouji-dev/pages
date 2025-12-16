"""add_language_to_users

Revision ID: 46fc6f4041c4
Revises: 0004
Create Date: 2025-12-16 14:39:13.395191

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "46fc6f4041c4"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add language column to users table."""
    # Add language column with default value 'en'
    op.add_column(
        "users",
        sa.Column(
            "language",
            sa.String(length=5),
            nullable=False,
            server_default="en",
        ),
    )
    # Create index on language for performance
    op.create_index(
        op.f("ix_users_language"),
        "users",
        ["language"],
        unique=False,
    )


def downgrade() -> None:
    """Remove language column from users table."""
    op.drop_index(op.f("ix_users_language"), table_name="users")
    op.drop_column("users", "language")
