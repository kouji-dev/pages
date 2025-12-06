"""Project repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Project


class ProjectRepository(ABC):
    """Abstract project repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, project: Project) -> Project:
        """Create a new project.

        Args:
            project: Project entity to create

        Returns:
            Created project with persisted data

        Raises:
            ConflictException: If project key already exists in organization
        """
        ...

    @abstractmethod
    async def get_by_id(self, project_id: UUID) -> Project | None:
        """Get project by ID.

        Args:
            project_id: Project UUID

        Returns:
            Project if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_key(self, organization_id: UUID, key: str) -> Project | None:
        """Get project by key within an organization.

        Args:
            organization_id: Organization UUID
            key: Project key

        Returns:
            Project if found, None otherwise
        """
        ...

    @abstractmethod
    async def update(self, project: Project) -> Project:
        """Update an existing project.

        Args:
            project: Project entity with updated data

        Returns:
            Updated project

        Raises:
            EntityNotFoundException: If project not found
            ConflictException: If key conflicts with another project in the organization
        """
        ...

    @abstractmethod
    async def delete(self, project_id: UUID) -> None:
        """Hard delete a project.

        Args:
            project_id: Project UUID

        Raises:
            EntityNotFoundException: If project not found
        """
        ...

    @abstractmethod
    async def exists_by_key(
        self, organization_id: UUID, key: str, exclude_id: UUID | None = None
    ) -> bool:
        """Check if project with key exists in organization.

        Args:
            organization_id: Organization UUID
            key: Project key to check
            exclude_id: Optional project ID to exclude from check

        Returns:
            True if project exists, False otherwise
        """
        ...

    @abstractmethod
    async def get_all(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
    ) -> list[Project]:
        """Get all projects in an organization with pagination.

        Args:
            organization_id: Organization UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted projects

        Returns:
            List of projects
        """
        ...

    @abstractmethod
    async def count(self, organization_id: UUID, include_deleted: bool = False) -> int:
        """Count total projects in an organization.

        Args:
            organization_id: Organization UUID
            include_deleted: Whether to include soft-deleted projects

        Returns:
            Total count of projects
        """
        ...

    @abstractmethod
    async def search(
        self,
        organization_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Project]:
        """Search projects by name or key within an organization.

        Args:
            organization_id: Organization UUID
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching projects
        """
        ...
