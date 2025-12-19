"""add_macros_table

Revision ID: 9b0c1d2e3f4a
Revises: 8a9b0c1d2e3f
Create Date: 2025-12-18 21:44:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9b0c1d2e3f4a"
down_revision: str | None = "8a9b0c1d2e3f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create macros table and add category to templates."""
    # Add category to templates table
    op.add_column("templates", sa.Column("category", sa.String(length=50), nullable=True))

    # Create macros table
    op.create_table(
        "macros",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("config_schema", sa.Text(), nullable=True),  # JSON schema
        sa.Column("macro_type", sa.String(length=50), nullable=False),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="false"),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_macro_name"),
    )
    op.create_index("ix_macros_macro_type", "macros", ["macro_type"])
    op.create_index("ix_macros_is_system", "macros", ["is_system"])


def downgrade() -> None:
    """Drop macros table and remove category from templates."""
    op.drop_index("ix_macros_is_system", table_name="macros")
    op.drop_index("ix_macros_macro_type", table_name="macros")
    op.drop_table("macros")
    op.drop_column("templates", "category")
