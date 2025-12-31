"""add_project_space_card_fields

Revision ID: f6618c83390b
Revises: 1581b495f287
Create Date: 2025-12-31 10:20:54.278196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6618c83390b'
down_revision: Union[str, None] = '1581b495f287'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add project and space card fields."""
    # Add project fields: color and status
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'projects' AND column_name = 'color'
            ) THEN
                ALTER TABLE projects ADD COLUMN color VARCHAR(7);
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'projects' AND column_name = 'status'
            ) THEN
                ALTER TABLE projects ADD COLUMN status VARCHAR(20) DEFAULT 'in-progress';
            END IF;
        END $$;
        """
    )

    # Add space fields: icon, status, view_count, created_by
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'spaces' AND column_name = 'icon'
            ) THEN
                ALTER TABLE spaces ADD COLUMN icon VARCHAR(50);
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'spaces' AND column_name = 'status'
            ) THEN
                ALTER TABLE spaces ADD COLUMN status VARCHAR(20) DEFAULT 'published';
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'spaces' AND column_name = 'view_count'
            ) THEN
                ALTER TABLE spaces ADD COLUMN view_count INTEGER DEFAULT 0 NOT NULL;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'spaces' AND column_name = 'created_by'
            ) THEN
                ALTER TABLE spaces ADD COLUMN created_by UUID;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE constraint_name = 'fk_spaces_created_by'
            ) THEN
                ALTER TABLE spaces ADD CONSTRAINT fk_spaces_created_by
                    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_spaces_created_by ON spaces(created_by);
        """
    )


def downgrade() -> None:
    """Remove project and space card fields."""
    # Remove space fields
    op.drop_index("ix_spaces_created_by", table_name="spaces")
    op.drop_constraint("fk_spaces_created_by", "spaces", type_="foreignkey")
    op.drop_column("spaces", "created_by")
    op.drop_column("spaces", "view_count")
    op.drop_column("spaces", "status")
    op.drop_column("spaces", "icon")

    # Remove project fields
    op.drop_column("projects", "status")
    op.drop_column("projects", "color")

