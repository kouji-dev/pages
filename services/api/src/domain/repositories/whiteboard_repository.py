"""Whiteboard repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Whiteboard


class WhiteboardRepository(ABC):
    """Abstract whiteboard repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, whiteboard: Whiteboard) -> Whiteboard:
        """Create a new whiteboard.

        Args:
            whiteboard: Whiteboard entity to create

        Returns:
            Created whiteboard with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, whiteboard_id: UUID) -> Whiteboard | None:
        """Get whiteboard by ID.

        Args:
            whiteboard_id: Whiteboard UUID

        Returns:
            Whiteboard if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_all(
        self,
        space_id: UUID,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
    ) -> list[Whiteboard]:
        """Get all whiteboards in a space with pagination.

        Args:
            space_id: Space UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted whiteboards

        Returns:
            List of whiteboards
        """
        ...

    @abstractmethod
    async def count(
        self,
        space_id: UUID,
        include_deleted: bool = False,
    ) -> int:
        """Count total whiteboards in a space.

        Args:
            space_id: Space UUID
            include_deleted: Whether to include soft-deleted whiteboards

        Returns:
            Total count of whiteboards
        """
        ...

    @abstractmethod
    async def update(self, whiteboard: Whiteboard) -> Whiteboard:
        """Update an existing whiteboard.

        Args:
            whiteboard: Whiteboard entity with updated data

        Returns:
            Updated whiteboard

        Raises:
            EntityNotFoundException: If whiteboard not found
        """
        ...

    @abstractmethod
    async def delete(self, whiteboard_id: UUID) -> None:
        """Hard delete a whiteboard.

        Args:
            whiteboard_id: Whiteboard UUID

        Raises:
            EntityNotFoundException: If whiteboard not found
        """
        ...
