"""Favorite repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Favorite
from src.domain.value_objects.entity_type import EntityType


class FavoriteRepository(ABC):
    """Abstract favorite repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, favorite: Favorite) -> Favorite:
        """Create a new favorite.

        Args:
            favorite: Favorite entity to create

        Returns:
            Created favorite with persisted data

        Raises:
            ConflictException: If favorite already exists (user + entity_type + entity_id)
        """
        ...

    @abstractmethod
    async def get_by_id(self, favorite_id: UUID) -> Favorite | None:
        """Get favorite by ID.

        Args:
            favorite_id: Favorite UUID

        Returns:
            Favorite if found, None otherwise
        """
        ...

    @abstractmethod
    async def delete(self, favorite_id: UUID) -> None:
        """Delete a favorite.

        Args:
            favorite_id: Favorite UUID

        Raises:
            EntityNotFoundException: If favorite not found
        """
        ...

    @abstractmethod
    async def get_all(
        self,
        user_id: UUID,
        entity_type: EntityType | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Favorite]:
        """Get all favorites for a user with optional filtering.

        Args:
            user_id: User UUID
            entity_type: Optional entity type to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of favorites
        """
        ...

    @abstractmethod
    async def count(
        self,
        user_id: UUID,
        entity_type: EntityType | None = None,
    ) -> int:
        """Count total favorites for a user.

        Args:
            user_id: User UUID
            entity_type: Optional entity type to filter by

        Returns:
            Total count of favorites
        """
        ...

    @abstractmethod
    async def exists(
        self,
        user_id: UUID,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> bool:
        """Check if favorite exists.

        Args:
            user_id: User UUID
            entity_type: Entity type
            entity_id: Entity ID

        Returns:
            True if favorite exists, False otherwise
        """
        ...

    @abstractmethod
    async def get_by_entity(
        self,
        user_id: UUID,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> Favorite | None:
        """Get favorite by user, entity type, and entity ID.

        Args:
            user_id: User UUID
            entity_type: Entity type
            entity_id: Entity ID

        Returns:
            Favorite if found, None otherwise
        """
        ...

