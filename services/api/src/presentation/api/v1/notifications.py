"""Notification management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.application.dtos.notification import (
    MarkAllAsReadResponse,
    MarkAsReadResponse,
    NotificationListResponse,
    UnreadCountResponse,
)
from src.application.use_cases.notification import (
    GetUnreadCountUseCase,
    ListNotificationsUseCase,
    MarkAllAsReadUseCase,
    MarkAsReadUseCase,
)
from src.domain.entities import User
from src.domain.repositories import NotificationRepository
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.services import get_notification_repository

router = APIRouter(tags=["Notifications"])


# Dependency injection for use cases
def get_list_notifications_use_case(
    notification_repository: Annotated[
        NotificationRepository, Depends(get_notification_repository)
    ],
) -> ListNotificationsUseCase:
    """Get list notifications use case with dependencies."""
    return ListNotificationsUseCase(notification_repository)


def get_mark_as_read_use_case(
    notification_repository: Annotated[
        NotificationRepository, Depends(get_notification_repository)
    ],
) -> MarkAsReadUseCase:
    """Get mark as read use case with dependencies."""
    return MarkAsReadUseCase(notification_repository)


def get_mark_all_as_read_use_case(
    notification_repository: Annotated[
        NotificationRepository, Depends(get_notification_repository)
    ],
) -> MarkAllAsReadUseCase:
    """Get mark all as read use case with dependencies."""
    return MarkAllAsReadUseCase(notification_repository)


def get_unread_count_use_case(
    notification_repository: Annotated[
        NotificationRepository, Depends(get_notification_repository)
    ],
) -> GetUnreadCountUseCase:
    """Get unread count use case with dependencies."""
    return GetUnreadCountUseCase(notification_repository)


@router.get(
    "/notifications",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List notifications",
    description="Get paginated list of notifications for the current user",
)
async def list_notifications(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListNotificationsUseCase, Depends(get_list_notifications_use_case)],
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(50, ge=1, le=100, description="Number of notifications per page"),
    read: bool | None = Query(None, description="Filter by read status (true/false/null for all)"),
) -> NotificationListResponse:
    """List notifications for the current user.

    Returns a paginated list of notifications. Can be filtered by read status.

    Args:
        current_user: Current authenticated user
        use_case: List notifications use case
        page: Page number (1-based)
        limit: Number of notifications per page (max 100)
        read: Optional filter by read status (None = all)

    Returns:
        NotificationListResponse: Paginated list of notifications
    """
    return await use_case.execute(
        user_id=str(current_user.id),
        page=page,
        limit=limit,
        read=read,
    )


@router.put(
    "/notifications/{notification_id}/read",
    response_model=MarkAsReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark notification as read",
    description="Mark a specific notification as read",
)
async def mark_notification_as_read(
    notification_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[MarkAsReadUseCase, Depends(get_mark_as_read_use_case)],
) -> MarkAsReadResponse:
    """Mark a notification as read.

    Args:
        notification_id: Notification ID
        current_user: Current authenticated user
        use_case: Mark as read use case

    Returns:
        MarkAsReadResponse: Updated notification status

    Raises:
        EntityNotFoundException: If notification not found
    """
    return await use_case.execute(notification_id)


@router.put(
    "/notifications/read-all",
    response_model=MarkAllAsReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark all notifications as read",
    description="Mark all unread notifications as read for the current user",
)
async def mark_all_notifications_as_read(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[MarkAllAsReadUseCase, Depends(get_mark_all_as_read_use_case)],
) -> MarkAllAsReadResponse:
    """Mark all notifications as read for the current user.

    Args:
        current_user: Current authenticated user
        use_case: Mark all as read use case

    Returns:
        MarkAllAsReadResponse: Number of notifications marked as read
    """
    return await use_case.execute(str(current_user.id))


@router.get(
    "/notifications/unread-count",
    response_model=UnreadCountResponse,
    status_code=status.HTTP_200_OK,
    summary="Get unread notification count",
    description="Get the count of unread notifications for the current user",
)
async def get_unread_notification_count(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetUnreadCountUseCase, Depends(get_unread_count_use_case)],
) -> UnreadCountResponse:
    """Get count of unread notifications for the current user.

    Args:
        current_user: Current authenticated user
        use_case: Get unread count use case

    Returns:
        UnreadCountResponse: Count of unread notifications
    """
    return await use_case.execute(str(current_user.id))
