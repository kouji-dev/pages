"""Mark all notifications as read use case."""

from uuid import UUID

import structlog

from src.application.dtos.notification import MarkAllAsReadResponse
from src.domain.repositories import NotificationRepository

logger = structlog.get_logger()


class MarkAllAsReadUseCase:
    """Use case for marking all notifications as read for a user."""

    def __init__(self, notification_repository: NotificationRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            notification_repository: Notification repository
        """
        self._notification_repository = notification_repository

    async def execute(self, user_id: str) -> MarkAllAsReadResponse:
        """Execute mark all notifications as read.

        Args:
            user_id: User ID

        Returns:
            Mark all as read response DTO
        """
        logger.info("Marking all notifications as read", user_id=user_id)

        user_uuid = UUID(user_id)

        # Mark all as read
        marked_count = await self._notification_repository.mark_all_as_read(user_uuid)

        logger.info(
            "All notifications marked as read",
            user_id=user_id,
            marked_count=marked_count,
        )

        return MarkAllAsReadResponse(marked_count=marked_count)
