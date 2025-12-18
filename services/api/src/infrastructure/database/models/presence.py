"""Presence tracking database model."""

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class PresenceModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Presence tracking database model.

    Tracks active users on pages for real-time collaboration.
    """

    __tablename__ = "presences"

    page_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cursor_position: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # JSON cursor position data
    selection: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # JSON selection data
    socket_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )  # WebSocket connection ID

    def __repr__(self) -> str:
        return f"<Presence(id={self.id}, page_id={self.page_id}, user_id={self.user_id})>"
