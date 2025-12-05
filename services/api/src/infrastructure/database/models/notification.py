"""Notification database model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class NotificationModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Notification database model.

    Stores user notifications for various events.
    """

    __tablename__ = "notifications"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Notification content
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # issue_assigned, issue_mentioned, comment_added, etc.
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Link to related entity
    entity_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # 'issue', 'page', 'comment', etc.
    entity_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )

    # Status
    read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # Metadata
    data: Mapped[str | None] = mapped_column(
        Text,  # Store as JSON string for additional data
        nullable=True,
    )

    # Relationships
    user = relationship(
        "UserModel",
        back_populates="notifications",
    )

    def __repr__(self) -> str:
        return (
            f"<Notification(id={self.id}, type={self.type}, user={self.user_id}, read={self.read})>"
        )
