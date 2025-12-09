"""Notification service for creating notifications."""

from uuid import UUID

import structlog

from src.domain.entities import Notification
from src.domain.repositories import NotificationRepository
from src.domain.value_objects.notification_type import NotificationType

logger = structlog.get_logger()


class NotificationService:
    """Service for creating and managing notifications.

    This service provides high-level methods for creating notifications
    for various events in the application (issue assignments, comments, mentions, etc.).
    """

    def __init__(self, notification_repository: NotificationRepository) -> None:
        """Initialize notification service.

        Args:
            notification_repository: Notification repository
        """
        self._notification_repository = notification_repository

    async def create_notification(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        content: str | None = None,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        data: dict | None = None,
    ) -> Notification:
        """Create a notification.

        Args:
            user_id: ID of the user receiving the notification
            notification_type: Type of notification
            title: Notification title
            content: Optional notification content
            entity_type: Optional type of related entity
            entity_id: Optional ID of related entity
            data: Optional additional metadata

        Returns:
            Created notification
        """
        logger.info(
            "Creating notification",
            user_id=user_id,
            type=notification_type.value,
            title=title,
        )

        notification = Notification.create(
            user_id=user_id,
            type=notification_type,
            title=title,
            content=content,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data,
        )

        created_notification = await self._notification_repository.create(notification)

        logger.info(
            "Notification created",
            notification_id=created_notification.id,
            user_id=user_id,
        )

        return created_notification

    async def notify_issue_assigned(
        self,
        assignee_id: UUID,
        issue_id: UUID,
        issue_title: str,
        assigned_by_name: str,
    ) -> Notification:
        """Create notification for issue assignment.

        Args:
            assignee_id: ID of user assigned to the issue
            issue_id: ID of the issue
            issue_title: Title of the issue
            assigned_by_name: Name of user who assigned the issue

        Returns:
            Created notification
        """
        return await self.create_notification(
            user_id=assignee_id,
            notification_type=NotificationType.ISSUE_ASSIGNED,
            title=f"You were assigned to: {issue_title}",
            content=f"{assigned_by_name} assigned you to this issue.",
            entity_type="issue",
            entity_id=issue_id,
            data={"issue_id": str(issue_id), "issue_title": issue_title},
        )

    async def notify_issue_commented(
        self,
        user_id: UUID,
        issue_id: UUID,
        issue_title: str,
        commenter_name: str,
        comment_preview: str,
    ) -> Notification:
        """Create notification for issue comment.

        Args:
            user_id: ID of user to notify
            issue_id: ID of the issue
            issue_title: Title of the issue
            commenter_name: Name of user who commented
            comment_preview: Preview of the comment content

        Returns:
            Created notification
        """
        return await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.ISSUE_COMMENTED,
            title=f"New comment on: {issue_title}",
            content=f"{commenter_name} commented: {comment_preview[:100]}...",
            entity_type="issue",
            entity_id=issue_id,
            data={"issue_id": str(issue_id), "issue_title": issue_title},
        )

    async def notify_issue_mentioned(
        self,
        user_id: UUID,
        issue_id: UUID,
        issue_title: str,
        mentioned_by_name: str,
    ) -> Notification:
        """Create notification for issue mention.

        Args:
            user_id: ID of mentioned user
            issue_id: ID of the issue
            issue_title: Title of the issue
            mentioned_by_name: Name of user who mentioned

        Returns:
            Created notification
        """
        return await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.ISSUE_MENTIONED,
            title=f"{mentioned_by_name} mentioned you in: {issue_title}",
            content=f"You were mentioned by {mentioned_by_name}.",
            entity_type="issue",
            entity_id=issue_id,
            data={"issue_id": str(issue_id), "issue_title": issue_title},
        )

    async def notify_issue_status_changed(
        self,
        user_id: UUID,
        issue_id: UUID,
        issue_title: str,
        old_status: str,
        new_status: str,
        changed_by_name: str,
    ) -> Notification:
        """Create notification for issue status change.

        Args:
            user_id: ID of user to notify
            issue_id: ID of the issue
            issue_title: Title of the issue
            old_status: Previous status
            new_status: New status
            changed_by_name: Name of user who changed status

        Returns:
            Created notification
        """
        return await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.ISSUE_STATUS_CHANGED,
            title=f"Status changed on: {issue_title}",
            content=f"{changed_by_name} changed status from {old_status} to {new_status}.",
            entity_type="issue",
            entity_id=issue_id,
            data={
                "issue_id": str(issue_id),
                "issue_title": issue_title,
                "old_status": old_status,
                "new_status": new_status,
            },
        )

    async def notify_page_commented(
        self,
        user_id: UUID,
        page_id: UUID,
        page_title: str,
        commenter_name: str,
        comment_preview: str,
    ) -> Notification:
        """Create notification for page comment.

        Args:
            user_id: ID of user to notify
            page_id: ID of the page
            page_title: Title of the page
            commenter_name: Name of user who commented
            comment_preview: Preview of the comment content

        Returns:
            Created notification
        """
        return await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.PAGE_COMMENTED,
            title=f"New comment on: {page_title}",
            content=f"{commenter_name} commented: {comment_preview[:100]}...",
            entity_type="page",
            entity_id=page_id,
            data={"page_id": str(page_id), "page_title": page_title},
        )

    async def notify_comment_mentioned(
        self,
        user_id: UUID,
        comment_id: UUID,
        entity_type: str,
        entity_id: UUID,
        entity_title: str,
        mentioned_by_name: str,
    ) -> Notification:
        """Create notification for comment mention.

        Args:
            user_id: ID of mentioned user
            comment_id: ID of the comment
            entity_type: Type of entity (issue, page)
            entity_id: ID of the entity
            entity_title: Title of the entity
            mentioned_by_name: Name of user who mentioned

        Returns:
            Created notification
        """
        return await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.COMMENT_MENTIONED,
            title=f"{mentioned_by_name} mentioned you in a comment",
            content=f"You were mentioned in a comment on: {entity_title}",
            entity_type=entity_type,
            entity_id=entity_id,
            data={
                "comment_id": str(comment_id),
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "entity_title": entity_title,
            },
        )
