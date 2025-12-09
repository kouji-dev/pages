"""Notification type value object."""

from enum import Enum


class NotificationType(str, Enum):
    """Notification types for user events.

    Defines the various types of notifications that can be sent to users.
    """

    # Issue-related notifications
    ISSUE_ASSIGNED = "issue_assigned"
    ISSUE_MENTIONED = "issue_mentioned"
    ISSUE_STATUS_CHANGED = "issue_status_changed"
    ISSUE_PRIORITY_CHANGED = "issue_priority_changed"
    ISSUE_COMMENTED = "issue_commented"

    # Page-related notifications
    PAGE_MENTIONED = "page_mentioned"
    PAGE_COMMENTED = "page_commented"
    PAGE_CREATED = "page_created"
    PAGE_UPDATED = "page_updated"

    # Comment-related notifications
    COMMENT_MENTIONED = "comment_mentioned"
    COMMENT_REPLIED = "comment_replied"

    # Organization-related notifications
    ORGANIZATION_INVITATION = "organization_invitation"
    ORGANIZATION_MEMBER_ADDED = "organization_member_added"
    ORGANIZATION_ROLE_CHANGED = "organization_role_changed"

    # Project-related notifications
    PROJECT_MEMBER_ADDED = "project_member_added"
    PROJECT_ROLE_CHANGED = "project_role_changed"

    def __str__(self) -> str:
        """Return the string value of the notification type."""
        return self.value
