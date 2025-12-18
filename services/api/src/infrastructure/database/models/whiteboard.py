"""Whiteboard database model."""

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class WhiteboardModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Whiteboard database model.

    Whiteboards are collaborative drawing canvases within spaces.
    """

    __tablename__ = "whiteboards"

    space_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("spaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    data: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # JSON data (drawings, shapes, text)
    created_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    space = relationship(
        "SpaceModel",
        back_populates="whiteboards",
    )
    creator = relationship(
        "UserModel",
        foreign_keys=[created_by],
    )
    updater = relationship(
        "UserModel",
        foreign_keys=[updated_by],
    )

    def __repr__(self) -> str:
        return f"<Whiteboard(id={self.id}, name={self.name}, space_id={self.space_id})>"
