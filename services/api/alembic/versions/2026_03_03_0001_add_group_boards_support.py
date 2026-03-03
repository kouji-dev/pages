"""add_group_boards_support

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-03

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: str | None = "b2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add organization_id and board_type to boards; create group_board_projects table."""
    op.add_column(
        "boards",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "boards",
        sa.Column("board_type", sa.String(20), nullable=False, server_default="project"),
    )
    op.create_foreign_key(
        "fk_boards_organization_id",
        "boards",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        op.f("ix_boards_organization_id"),
        "boards",
        ["organization_id"],
        unique=False,
    )

    op.create_table(
        "group_board_projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("group_board_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["group_board_id"], ["boards.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_group_board_projects_group_board_id"),
        "group_board_projects",
        ["group_board_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_group_board_projects_project_id"),
        "group_board_projects",
        ["project_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove group_board_projects and board columns."""
    op.drop_index(
        op.f("ix_group_board_projects_project_id"),
        table_name="group_board_projects",
    )
    op.drop_index(
        op.f("ix_group_board_projects_group_board_id"),
        table_name="group_board_projects",
    )
    op.drop_table("group_board_projects")

    op.drop_index(op.f("ix_boards_organization_id"), table_name="boards")
    op.drop_constraint("fk_boards_organization_id", "boards", type_="foreignkey")
    op.drop_column("boards", "board_type")
    op.drop_column("boards", "organization_id")
