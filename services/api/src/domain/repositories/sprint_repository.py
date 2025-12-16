"""Sprint repository interface (port)."""

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from src.domain.entities import Sprint
from src.domain.value_objects.sprint_status import SprintStatus


class SprintRepository(ABC):
    """Abstract sprint repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, sprint: Sprint) -> Sprint:
        """Create a new sprint.

        Args:
            sprint: Sprint entity to create

        Returns:
            Created sprint with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, sprint_id: UUID) -> Sprint | None:
        """Get sprint by ID.

        Args:
            sprint_id: Sprint UUID

        Returns:
            Sprint if found, None otherwise
        """
        ...

    @abstractmethod
    async def update(self, sprint: Sprint) -> Sprint:
        """Update an existing sprint.

        Args:
            sprint: Sprint entity with updated data

        Returns:
            Updated sprint

        Raises:
            EntityNotFoundException: If sprint not found
        """
        ...

    @abstractmethod
    async def delete(self, sprint_id: UUID) -> None:
        """Hard delete a sprint.

        Args:
            sprint_id: Sprint UUID

        Raises:
            EntityNotFoundException: If sprint not found
        """
        ...

    @abstractmethod
    async def get_all(
        self,
        project_id: UUID,
        page: int = 1,
        limit: int = 20,
        status: SprintStatus | None = None,
        include_deleted: bool = False,
    ) -> list[Sprint]:
        """Get all sprints in a project with filters and pagination.

        Args:
            project_id: Project UUID to filter by
            page: Page number (1-indexed)
            limit: Maximum number of records to return
            status: Optional status filter
            include_deleted: Whether to include soft-deleted sprints

        Returns:
            List of sprints
        """
        ...

    @abstractmethod
    async def count(
        self,
        project_id: UUID,
        status: SprintStatus | None = None,
        include_deleted: bool = False,
    ) -> int:
        """Count total sprints in a project with filters.

        Args:
            project_id: Project UUID to filter by
            status: Optional status filter
            include_deleted: Whether to include soft-deleted sprints

        Returns:
            Total count of sprints
        """
        ...

    @abstractmethod
    async def find_overlapping_sprints(
        self,
        project_id: UUID,
        start_date: date,
        end_date: date,
        exclude_sprint_id: UUID | None = None,
    ) -> list[Sprint]:
        """Find sprints that overlap with the given date range.

        Args:
            project_id: Project UUID to filter by
            start_date: Start date of the date range
            end_date: End date of the date range
            exclude_sprint_id: Optional sprint ID to exclude from results

        Returns:
            List of overlapping sprints
        """
        ...

    @abstractmethod
    async def get_active_sprint(self, project_id: UUID) -> Sprint | None:
        """Get the active sprint for a project.

        Args:
            project_id: Project UUID

        Returns:
            Active sprint if found, None otherwise
        """
        ...

    @abstractmethod
    async def add_issue_to_sprint(
        self,
        sprint_id: UUID,
        issue_id: UUID,
        order: int,
    ) -> None:
        """Add an issue to a sprint.

        Args:
            sprint_id: Sprint UUID
            issue_id: Issue UUID
            order: Order within the sprint

        Raises:
            EntityNotFoundException: If sprint or issue not found
            ConflictException: If issue is already in the sprint
        """
        ...

    @abstractmethod
    async def remove_issue_from_sprint(
        self,
        sprint_id: UUID,
        issue_id: UUID,
    ) -> None:
        """Remove an issue from a sprint.

        Args:
            sprint_id: Sprint UUID
            issue_id: Issue UUID

        Raises:
            EntityNotFoundException: If sprint or issue not found
        """
        ...

    @abstractmethod
    async def reorder_sprint_issues(
        self,
        sprint_id: UUID,
        issue_orders: dict[UUID, int],
    ) -> None:
        """Reorder issues within a sprint.

        Args:
            sprint_id: Sprint UUID
            issue_orders: Dictionary mapping issue IDs to their new order

        Raises:
            EntityNotFoundException: If sprint not found
        """
        ...

    @abstractmethod
    async def get_sprint_issues(
        self,
        sprint_id: UUID,
    ) -> list[tuple[UUID, int]]:
        """Get all issues in a sprint with their order.

        Args:
            sprint_id: Sprint UUID

        Returns:
            List of tuples (issue_id, order)
        """
        ...

    @abstractmethod
    async def get_issue_sprint(self, issue_id: UUID) -> Sprint | None:
        """Get the sprint that contains an issue.

        Args:
            issue_id: Issue UUID

        Returns:
            Sprint if found, None otherwise
        """
        ...
