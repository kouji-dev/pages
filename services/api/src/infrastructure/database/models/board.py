"""Board and BoardList database models."""

from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class BoardModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Board database model.

    Boards belong to a project and define a view over issues with configurable
    columns (lists) and optional scope.
    """

    __tablename__ = "boards"

    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    scope_config: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    is_default: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    board_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="project",
    )  # 'project' or 'group'
    swimlane_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="none",
    )  # 'none', 'epic', 'assignee'
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    created_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    project = relationship(
        "ProjectModel",
        back_populates="boards",
    )
    lists = relationship(
        "BoardListModel",
        back_populates="board",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="BoardListModel.position",
    )

    def __repr__(self) -> str:
        return (
            f"<Board(id={self.id}, name={self.name}, project_id={self.project_id}, "
            f"organization_id={self.organization_id}, board_type={self.board_type})>"
        )


class BoardListModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Board list (column) database model.

    Each list has a type (label, assignee, milestone) and config (e.g. label_id).
    """

    __tablename__ = "board_lists"

    board_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    list_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # 'label', 'assignee', 'milestone'
    list_config: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Relationships
    board = relationship(
        "BoardModel",
        back_populates="lists",
    )

    def __repr__(self) -> str:
        return f"<BoardList(id={self.id}, board_id={self.board_id}, list_type={self.list_type})>"


class GroupBoardProjectModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Mapping between a group board and its projects (ordered)."""

    __tablename__ = "group_board_projects"

    group_board_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    def __repr__(self) -> str:
        return (
            f"<GroupBoardProject(id={self.id}, group_board_id={self.group_board_id}, "
            f"project_id={self.project_id}, position={self.position})>"
        )
