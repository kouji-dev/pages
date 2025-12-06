"""Issue activity repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.infrastructure.database.models import IssueActivityModel


class IssueActivityRepository(ABC):
    """Abstract issue activity repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(
        self,
        issue_id: UUID,
        user_id: UUID | None,
        action: str,
        field_name: str | None = None,
        old_value: str | None = None,
        new_value: str | None = None,
    ) -> IssueActivityModel:
        """Create a new activity log entry.

        Args:
            issue_id: Issue UUID
            user_id: User UUID who performed the action (can be None for system actions)
            action: Action type (created, updated, deleted, status_changed, etc.)
            field_name: Optional field name that was changed
            old_value: Optional old value (as string)
            new_value: Optional new value (as string)

        Returns:
            Created activity model
        """
        ...

    @abstractmethod
    async def get_by_issue_id(
        self,
        issue_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[IssueActivityModel]:
        """Get all activities for an issue.

        Args:
            issue_id: Issue UUID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of activity models, ordered by created_at DESC
        """
        ...

    @abstractmethod
    async def count_by_issue_id(self, issue_id: UUID) -> int:
        """Count total activities for an issue.

        Args:
            issue_id: Issue UUID

        Returns:
            Total count of activities
        """
        ...
