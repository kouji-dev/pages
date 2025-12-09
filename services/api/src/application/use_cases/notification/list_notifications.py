"""List notifications use case."""

from math import ceil
from uuid import UUID

import structlog

from src.application.dtos.notification import (
    NotificationListItemResponse,
    NotificationListResponse,
)
from src.domain.repositories import NotificationRepository

logger = structlog.get_logger()


class ListNotificationsUseCase:
    """Use case for listing user notifications."""

    def __init__(self, notification_repository: NotificationRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            notification_repository: Notification repository
        """
        self._notification_repository = notification_repository

    async def execute(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 50,
        read: bool | None = None,
    ) -> NotificationListResponse:
        """Execute list notifications.

        Args:
            user_id: User ID
            page: Page number (1-based)
            limit: Number of notifications per page
            read: Filter by read status (None = all, True = read only, False = unread only)

        Returns:
            Notification list response DTO
        """
        logger.info(
            "Listing notifications",
            user_id=user_id,
            page=page,
            limit=limit,
            read=read,
        )

        user_uuid = UUID(user_id)
        skip = (page - 1) * limit

        # Get notifications and total count
        notifications = await self._notification_repository.get_by_user_id(
            user_uuid, skip=skip, limit=limit, read=read
        )
        total = await self._notification_repository.count_by_user_id(user_uuid, read=read)

        # Calculate total pages
        pages = ceil(total / limit) if total > 0 else 1

        logger.info(
            "Notifications listed",
            user_id=user_id,
            count=len(notifications),
            total=total,
        )

        # Convert to response DTOs
        notification_items = [
            NotificationListItemResponse(
                id=n.id,
                type=n.type,
                title=n.title,
                content=n.content,
                entity_type=n.entity_type,
                entity_id=n.entity_id,
                read=n.read,
                created_at=n.created_at,
            )
            for n in notifications
        ]

        return NotificationListResponse(
            notifications=notification_items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )
