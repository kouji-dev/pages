"""Organization repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Organization


class OrganizationRepository(ABC):
    """Abstract organization repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, organization: Organization) -> Organization:
        """Create a new organization.

        Args:
            organization: Organization entity to create

        Returns:
            Created organization with persisted data

        Raises:
            ConflictException: If slug already exists
        """
        ...

    @abstractmethod
    async def get_by_id(self, organization_id: UUID) -> Organization | None:
        """Get organization by ID.

        Args:
            organization_id: Organization UUID

        Returns:
            Organization if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Organization | None:
        """Get organization by slug.

        Args:
            slug: Organization slug

        Returns:
            Organization if found, None otherwise
        """
        ...

    @abstractmethod
    async def update(self, organization: Organization) -> Organization:
        """Update an existing organization.

        Args:
            organization: Organization entity with updated data

        Returns:
            Updated organization

        Raises:
            EntityNotFoundException: If organization not found
            ConflictException: If slug conflicts with another organization
        """
        ...

    @abstractmethod
    async def delete(self, organization_id: UUID) -> None:
        """Hard delete an organization.

        Args:
            organization_id: Organization UUID

        Raises:
            EntityNotFoundException: If organization not found
        """
        ...

    @abstractmethod
    async def exists_by_slug(self, slug: str, exclude_id: UUID | None = None) -> bool:
        """Check if organization with slug exists.

        Args:
            slug: Slug to check
            exclude_id: Optional organization ID to exclude from check

        Returns:
            True if organization exists, False otherwise
        """
        ...

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
        user_id: UUID | None = None,
    ) -> list[Organization]:
        """Get all organizations with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted organizations
            user_id: Optional user ID to filter organizations by membership

        Returns:
            List of organizations
        """
        ...

    @abstractmethod
    async def count(
        self, include_deleted: bool = False, user_id: UUID | None = None
    ) -> int:
        """Count total organizations.

        Args:
            include_deleted: Whether to include soft-deleted organizations
            user_id: Optional user ID to count only organizations where user is a member

        Returns:
            Total count of organizations
        """
        ...

    @abstractmethod
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
        user_id: UUID | None = None,
    ) -> list[Organization]:
        """Search organizations by name or slug.

        Args:
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return
            user_id: Optional user ID to filter organizations by membership

        Returns:
            List of matching organizations
        """
        ...

