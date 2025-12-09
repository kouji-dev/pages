"""Notification domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Self
from uuid import UUID, uuid4

from src.domain.value_objects.notification_type import NotificationType


@dataclass
class Notification:
    """Notification domain entity.

    Represents a notification sent to a user about various events.
    """

    id: UUID
    user_id: UUID
    type: NotificationType
    title: str
    content: str | None = None
    entity_type: str | None = None  # 'issue', 'page', 'comment', etc.
    entity_id: UUID | None = None
    read: bool = False
    data: dict[str, Any] | None = None  # Additional metadata
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate notification entity."""
        if not self.title or not self.title.strip():
            raise ValueError("Notification title cannot be empty")

        self.title = self.title.strip()

        if len(self.title) > 255:
            raise ValueError("Notification title cannot exceed 255 characters")

        if self.content and len(self.content) > 5000:
            raise ValueError("Notification content cannot exceed 5000 characters")

        valid_entity_types = {"issue", "page", "comment", "organization", "project"}
        if self.entity_type and self.entity_type not in valid_entity_types:
            raise ValueError(f"Entity type must be one of: {', '.join(valid_entity_types)}")

        # If entity_type is set, entity_id must also be set
        if self.entity_type and not self.entity_id:
            raise ValueError("entity_id must be set when entity_type is provided")

        if self.entity_id and not self.entity_type:
            raise ValueError("entity_type must be set when entity_id is provided")

    @classmethod
    def create(
        cls,
        user_id: UUID,
        type: NotificationType,
        title: str,
        content: str | None = None,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        data: dict[str, Any] | None = None,
    ) -> Self:
        """Create a new notification.

        Factory method for creating new notifications.

        Args:
            user_id: ID of the user receiving the notification
            type: Type of notification
            title: Notification title (required, max 255 characters)
            content: Optional notification content (max 5000 characters)
            entity_type: Optional type of related entity ('issue', 'page', etc.)
            entity_id: Optional ID of related entity
            data: Optional additional metadata as dict

        Returns:
            New Notification instance

        Raises:
            ValueError: If title or other fields are invalid
        """
        return cls(
            id=uuid4(),
            user_id=user_id,
            type=type,
            title=title,
            content=content,
            entity_type=entity_type,
            entity_id=entity_id,
            read=False,
            data=data,
            created_at=datetime.utcnow(),
        )

    def mark_as_read(self) -> None:
        """Mark notification as read."""
        self.read = True

    def is_unread(self) -> bool:
        """Check if notification is unread."""
        return not self.read
