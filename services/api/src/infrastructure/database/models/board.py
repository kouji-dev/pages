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
        return f"<Board(id={self.id}, name={self.name}, project_id={self.project_id})>"


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
