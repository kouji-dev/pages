"""Get unread notification count use case."""

from uuid import UUID

import structlog

from src.application.dtos.notification import UnreadCountResponse
from src.domain.repositories import NotificationRepository

logger = structlog.get_logger()


class GetUnreadCountUseCase:
    """Use case for getting count of unread notifications."""

    def __init__(self, notification_repository: NotificationRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            notification_repository: Notification repository
        """
        self._notification_repository = notification_repository

    async def execute(self, user_id: str) -> UnreadCountResponse:
        """Execute get unread count.

        Args:
            user_id: User ID

        Returns:
            Unread count response DTO
        """
        logger.info("Getting unread notification count", user_id=user_id)

        user_uuid = UUID(user_id)

        # Get unread count
        unread_count = await self._notification_repository.count_unread(user_uuid)

        logger.info(
            "Unread notification count retrieved",
            user_id=user_id,
            unread_count=unread_count,
        )

        return UnreadCountResponse(unread_count=unread_count)
