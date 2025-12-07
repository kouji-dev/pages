"""Space repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Space


class SpaceRepository(ABC):
    """Abstract space repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, space: Space) -> Space:
        """Create a new space.

        Args:
            space: Space entity to create

        Returns:
            Created space with persisted data

        Raises:
            ConflictException: If space key already exists in organization
        """
        ...

    @abstractmethod
    async def get_by_id(self, space_id: UUID) -> Space | None:
        """Get space by ID.

        Args:
            space_id: Space UUID

        Returns:
            Space if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_key(self, organization_id: UUID, key: str) -> Space | None:
        """Get space by key within an organization.

        Args:
            organization_id: Organization UUID
            key: Space key

        Returns:
            Space if found, None otherwise
        """
        ...

    @abstractmethod
    async def update(self, space: Space) -> Space:
        """Update an existing space.

        Args:
            space: Space entity with updated data

        Returns:
            Updated space

        Raises:
            EntityNotFoundException: If space not found
            ConflictException: If key conflicts with another space in the organization
        """
        ...

    @abstractmethod
    async def delete(self, space_id: UUID) -> None:
        """Hard delete a space.

        Args:
            space_id: Space UUID

        Raises:
            EntityNotFoundException: If space not found
        """
        ...

    @abstractmethod
    async def exists_by_key(
        self, organization_id: UUID, key: str, exclude_id: UUID | None = None
    ) -> bool:
        """Check if space with key exists in organization.

        Args:
            organization_id: Organization UUID
            key: Space key to check
            exclude_id: Optional space ID to exclude from check

        Returns:
            True if space exists, False otherwise
        """
        ...

    @abstractmethod
    async def get_all(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
    ) -> list[Space]:
        """Get all spaces in an organization with pagination.

        Args:
            organization_id: Organization UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted spaces

        Returns:
            List of spaces
        """
        ...

    @abstractmethod
    async def count(self, organization_id: UUID, include_deleted: bool = False) -> int:
        """Count total spaces in an organization.

        Args:
            organization_id: Organization UUID
            include_deleted: Whether to include soft-deleted spaces

        Returns:
            Total count of spaces
        """
        ...

    @abstractmethod
    async def search(
        self,
        organization_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Space]:
        """Search spaces by name or key within an organization.

        Args:
            organization_id: Organization UUID
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching spaces
        """
        ...
