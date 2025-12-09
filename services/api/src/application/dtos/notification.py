"""Notification DTOs."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.value_objects.notification_type import NotificationType


class NotificationResponse(BaseModel):
    """Response DTO for notification data."""

    id: UUID
    user_id: UUID
    type: NotificationType = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    content: str | None = Field(None, description="Optional notification content")
    entity_type: str | None = Field(
        None, description="Related entity type (issue, page, comment, etc.)"
    )
    entity_id: UUID | None = Field(None, description="Related entity ID")
    read: bool = Field(default=False, description="Whether the notification has been read")
    data: dict[str, Any] | None = Field(None, description="Additional metadata")
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
        use_enum_values = False


class NotificationListItemResponse(BaseModel):
    """Response DTO for notification in list view."""

    id: UUID
    type: NotificationType
    title: str
    content: str | None = None
    entity_type: str | None = None
    entity_id: UUID | None = None
    read: bool
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
        use_enum_values = False


class NotificationListResponse(BaseModel):
    """Response DTO for list of notifications."""

    notifications: list[NotificationListItemResponse] = Field(
        ..., description="List of notifications"
    )
    total: int = Field(..., description="Total number of notifications")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class UnreadCountResponse(BaseModel):
    """Response DTO for unread notification count."""

    unread_count: int = Field(..., description="Number of unread notifications")


class MarkAsReadResponse(BaseModel):
    """Response DTO for mark as read operation."""

    id: UUID
    read: bool = Field(default=True, description="Read status after marking")


class MarkAllAsReadResponse(BaseModel):
    """Response DTO for mark all as read operation."""

    marked_count: int = Field(..., description="Number of notifications marked as read")
