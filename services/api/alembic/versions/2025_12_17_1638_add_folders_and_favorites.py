"""add_folders_and_favorites

Revision ID: a1b2c3d4e5f6
Revises: db2589b32856
Create Date: 2025-12-17 16:38:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1432f294aabb"
down_revision: str | None = "db2589b32856"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create folders and favorites tables, add folder_id to projects and spaces."""
    # Create folders table
    op.create_table(
        "folders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["folders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_folders_organization_id", "folders", ["organization_id"])
    op.create_index("ix_folders_parent_id", "folders", ["parent_id"])

    # Create favorites table
    op.create_table(
        "favorites",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(length=20), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "entity_type", "entity_id", name="uq_favorite"),
    )
    op.create_index("ix_favorites_user_id", "favorites", ["user_id"])
    op.create_index("ix_favorites_entity_type", "favorites", ["entity_type"])
    op.create_index("ix_favorites_entity_id", "favorites", ["entity_id"])

    # Add folder_id to projects table
    op.add_column(
        "projects",
        sa.Column("folder_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_projects_folder_id",
        "projects",
        "folders",
        ["folder_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_projects_folder_id", "projects", ["folder_id"])

    # Add folder_id to spaces table
    op.add_column(
        "spaces",
        sa.Column("folder_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_spaces_folder_id",
        "spaces",
        "folders",
        ["folder_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_spaces_folder_id", "spaces", ["folder_id"])


def downgrade() -> None:
    """Drop folders and favorites tables, remove folder_id from projects and spaces."""
    # Remove folder_id from spaces
    op.drop_index("ix_spaces_folder_id", table_name="spaces")
    op.drop_constraint("fk_spaces_folder_id", "spaces", type_="foreignkey")
    op.drop_column("spaces", "folder_id")

    # Remove folder_id from projects
    op.drop_index("ix_projects_folder_id", table_name="projects")
    op.drop_constraint("fk_projects_folder_id", "projects", type_="foreignkey")
    op.drop_column("projects", "folder_id")

    # Drop favorites table
    op.drop_index("ix_favorites_entity_id", table_name="favorites")
    op.drop_index("ix_favorites_entity_type", table_name="favorites")
    op.drop_index("ix_favorites_user_id", table_name="favorites")
    op.drop_table("favorites")

    # Drop folders table
    op.drop_index("ix_folders_parent_id", table_name="folders")
    op.drop_index("ix_folders_organization_id", table_name="folders")
    op.drop_table("folders")
