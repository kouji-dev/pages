"""Notification repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Notification


class NotificationRepository(ABC):
    """Abstract notification repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, notification: Notification) -> Notification:
        """Create a new notification.

        Args:
            notification: Notification entity to create

        Returns:
            Created notification with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, notification_id: UUID) -> Notification | None:
        """Get notification by ID.

        Args:
            notification_id: Notification UUID

        Returns:
            Notification if found, None otherwise
        """
        ...

    @abstractmethod
    async def update(self, notification: Notification) -> Notification:
        """Update an existing notification.

        Args:
            notification: Notification entity with updated data

        Returns:
            Updated notification

        Raises:
            EntityNotFoundException: If notification not found
        """
        ...

    @abstractmethod
    async def delete(self, notification_id: UUID) -> None:
        """Hard delete a notification.

        Args:
            notification_id: Notification UUID

        Raises:
            EntityNotFoundException: If notification not found
        """
        ...

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        read: bool | None = None,
    ) -> list[Notification]:
        """Get all notifications for a user.

        Args:
            user_id: User UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            read: Filter by read status (None = all, True = read only, False = unread only)

        Returns:
            List of notifications, ordered by created_at DESC
        """
        ...

    @abstractmethod
    async def count_by_user_id(self, user_id: UUID, read: bool | None = None) -> int:
        """Count total notifications for a user.

        Args:
            user_id: User UUID
            read: Filter by read status (None = all, True = read only, False = unread only)

        Returns:
            Total count of notifications
        """
        ...

    @abstractmethod
    async def mark_as_read(self, notification_id: UUID) -> Notification:
        """Mark notification as read.

        Args:
            notification_id: Notification UUID

        Returns:
            Updated notification

        Raises:
            EntityNotFoundException: If notification not found
        """
        ...

    @abstractmethod
    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user.

        Args:
            user_id: User UUID

        Returns:
            Number of notifications marked as read
        """
        ...

    @abstractmethod
    async def count_unread(self, user_id: UUID) -> int:
        """Count unread notifications for a user.

        Args:
            user_id: User UUID

        Returns:
            Count of unread notifications
        """
        ...
