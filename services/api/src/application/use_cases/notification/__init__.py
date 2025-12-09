"""Notification use cases."""

from src.application.use_cases.notification.get_unread_count import (
    GetUnreadCountUseCase,
)
from src.application.use_cases.notification.list_notifications import (
    ListNotificationsUseCase,
)
from src.application.use_cases.notification.mark_all_as_read import (
    MarkAllAsReadUseCase,
)
from src.application.use_cases.notification.mark_as_read import MarkAsReadUseCase

__all__ = [
    "ListNotificationsUseCase",
    "MarkAsReadUseCase",
    "MarkAllAsReadUseCase",
    "GetUnreadCountUseCase",
]
