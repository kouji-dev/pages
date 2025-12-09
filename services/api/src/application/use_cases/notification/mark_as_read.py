"""Mark notification as read use case."""

from uuid import UUID

import structlog

from src.application.dtos.notification import MarkAsReadResponse
from src.domain.repositories import NotificationRepository

logger = structlog.get_logger()


class MarkAsReadUseCase:
    """Use case for marking a notification as read."""

    def __init__(self, notification_repository: NotificationRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            notification_repository: Notification repository
        """
        self._notification_repository = notification_repository

    async def execute(self, notification_id: str) -> MarkAsReadResponse:
        """Execute mark notification as read.

        Args:
            notification_id: Notification ID

        Returns:
            Mark as read response DTO

        Raises:
            EntityNotFoundException: If notification not found
        """
        logger.info("Marking notification as read", notification_id=notification_id)

        notification_uuid = UUID(notification_id)

        # Mark as read (will raise EntityNotFoundException if not found)
        notification = await self._notification_repository.mark_as_read(notification_uuid)

        logger.info("Notification marked as read", notification_id=notification_id)

        return MarkAsReadResponse(
            id=notification.id,
            read=notification.read,
        )
