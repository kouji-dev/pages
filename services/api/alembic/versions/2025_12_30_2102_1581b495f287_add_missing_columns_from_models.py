"""add_missing_columns_from_models

Revision ID: 1581b495f287
Revises: 43e25464cdbc
Create Date: 2025-12-30 21:02:51.843728

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1581b495f287"
down_revision: str | None = "43e25464cdbc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add missing columns that should exist according to SQLAlchemy models.

    This migration adds columns that were defined in models but missing from
    the database. It uses conditional SQL to avoid errors if columns already exist.
    """
    # Users.language (from migration 46fc6f4041c4, but may not have been applied)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'language'
            ) THEN
                ALTER TABLE users ADD COLUMN language VARCHAR(5) NOT NULL DEFAULT 'en';
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_users_language ON users(language);
        """
    )

    # Issues.backlog_order (from migration add_sprints_backlog)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'issues' AND column_name = 'backlog_order'
            ) THEN
                ALTER TABLE issues ADD COLUMN backlog_order INTEGER;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_issues_backlog_order ON issues(backlog_order);
        """
    )

    # Issues.parent_issue_id (from migration 3c8bea2ce013)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'issues' AND column_name = 'parent_issue_id'
            ) THEN
                ALTER TABLE issues ADD COLUMN parent_issue_id UUID;
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
                WHERE constraint_name = 'fk_issues_parent_issue_id'
            ) THEN
                ALTER TABLE issues ADD CONSTRAINT fk_issues_parent_issue_id 
                    FOREIGN KEY (parent_issue_id) REFERENCES issues(id) ON DELETE SET NULL;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_issues_parent_issue_id ON issues(parent_issue_id);
        """
    )

    # Projects.folder_id (from migration 1432f294aabb)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'projects' AND column_name = 'folder_id'
            ) THEN
                ALTER TABLE projects ADD COLUMN folder_id UUID;
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
                WHERE constraint_name = 'fk_projects_folder_id'
            ) THEN
                ALTER TABLE projects ADD CONSTRAINT fk_projects_folder_id 
                    FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_projects_folder_id ON projects(folder_id);
        """
    )

    # Spaces.folder_id (from migration 1432f294aabb)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'spaces' AND column_name = 'folder_id'
            ) THEN
                ALTER TABLE spaces ADD COLUMN folder_id UUID;
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
                WHERE constraint_name = 'fk_spaces_folder_id'
            ) THEN
                ALTER TABLE spaces ADD CONSTRAINT fk_spaces_folder_id 
                    FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_spaces_folder_id ON spaces(folder_id);
        """
    )

    # Templates.category (from migration 9b0c1d2e3f4a)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'templates' AND column_name = 'category'
            ) THEN
                ALTER TABLE templates ADD COLUMN category VARCHAR(50);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    """Remove columns added by this migration."""
    # Templates.category
    op.drop_column("templates", "category")

    # Spaces.folder_id
    op.drop_index("ix_spaces_folder_id", table_name="spaces")
    op.drop_constraint("fk_spaces_folder_id", "spaces", type_="foreignkey")
    op.drop_column("spaces", "folder_id")

    # Projects.folder_id
    op.drop_index("ix_projects_folder_id", table_name="projects")
    op.drop_constraint("fk_projects_folder_id", "projects", type_="foreignkey")
    op.drop_column("projects", "folder_id")

    # Issues.parent_issue_id
    op.drop_index("ix_issues_parent_issue_id", table_name="issues")
    op.drop_constraint("fk_issues_parent_issue_id", "issues", type_="foreignkey")
    op.drop_column("issues", "parent_issue_id")

    # Issues.backlog_order
    op.drop_index("ix_issues_backlog_order", table_name="issues")
    op.drop_column("issues", "backlog_order")

    # Users.language
    op.drop_index("ix_users_language", table_name="users")
    op.drop_column("users", "language")
