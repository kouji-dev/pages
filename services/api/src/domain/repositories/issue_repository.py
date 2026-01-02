"""Issue repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Issue


class IssueRepository(ABC):
    """Abstract issue repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def get_next_issue_number(self, project_id: UUID) -> int:
        """Get the next issue number for a project.

        This should be atomic to ensure no duplicates.

        Args:
            project_id: Project UUID

        Returns:
            Next issue number (starting from 1)
        """
        ...

    @abstractmethod
    async def create(self, issue: Issue) -> Issue:
        """Create a new issue.

        Args:
            issue: Issue entity to create

        Returns:
            Created issue with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, issue_id: UUID) -> Issue | None:
        """Get issue by ID.

        Args:
            issue_id: Issue UUID

        Returns:
            Issue if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_key(self, project_key: str, issue_number: int) -> Issue | None:
        """Get issue by project key and issue number.

        Args:
            project_key: Project key (e.g., "PROJ")
            issue_number: Issue number (e.g., 123)

        Returns:
            Issue if found, None otherwise
        """
        ...

    @abstractmethod
    async def update(self, issue: Issue) -> Issue:
        """Update an existing issue.

        Args:
            issue: Issue entity with updated data

        Returns:
            Updated issue

        Raises:
            EntityNotFoundException: If issue not found
        """
        ...

    @abstractmethod
    async def delete(self, issue_id: UUID) -> None:
        """Hard delete an issue.

        Args:
            issue_id: Issue UUID

        Raises:
            EntityNotFoundException: If issue not found
        """
        ...

    @abstractmethod
    async def get_all(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
        assignee_id: UUID | None = None,
        reporter_id: UUID | None = None,
        status: str | None = None,
        type: str | None = None,
        priority: str | None = None,
        sprint_id: UUID | None = None,
    ) -> list[Issue]:
        """Get all issues in a project with filters and pagination.

        Args:
            project_id: Project UUID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted issues
            assignee_id: Optional assignee filter
            reporter_id: Optional reporter filter
            status: Optional status filter
            type: Optional type filter
            priority: Optional priority filter
            sprint_id: Optional sprint filter

        Returns:
            List of issues
        """
        ...

    @abstractmethod
    async def count(
        self,
        project_id: UUID,
        include_deleted: bool = False,
        assignee_id: UUID | None = None,
        reporter_id: UUID | None = None,
        status: str | None = None,
        type: str | None = None,
        priority: str | None = None,
        sprint_id: UUID | None = None,
    ) -> int:
        """Count total issues in a project with filters.

        Args:
            project_id: Project UUID to filter by
            include_deleted: Whether to include soft-deleted issues
            assignee_id: Optional assignee filter
            reporter_id: Optional reporter filter
            status: Optional status filter
            type: Optional type filter
            priority: Optional priority filter
            sprint_id: Optional sprint filter

        Returns:
            Total count of issues
        """
        ...

    @abstractmethod
    async def search(
        self,
        project_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Issue]:
        """Search issues by title or description within a project.

        Args:
            project_id: Project UUID to filter by
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching issues
        """
        ...
