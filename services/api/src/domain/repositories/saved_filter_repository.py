"""Saved filter repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.saved_filter import SavedFilter


class SavedFilterRepository(ABC):
    """Abstract saved filter repository interface."""

    @abstractmethod
    async def create(self, saved_filter: SavedFilter) -> SavedFilter:
        """Create a new saved filter."""
        ...

    @abstractmethod
    async def get_by_id(self, filter_id: UUID) -> SavedFilter | None:
        """Get saved filter by ID."""
        ...

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list[SavedFilter]:
        """Get all saved filters for a user."""
        ...

    @abstractmethod
    async def get_by_user_and_project(self, user_id: UUID, project_id: UUID) -> list[SavedFilter]:
        """Get all saved filters for a user in a project."""
        ...

    @abstractmethod
    async def update(self, saved_filter: SavedFilter) -> SavedFilter:
        """Update an existing saved filter."""
        ...

    @abstractmethod
    async def delete(self, filter_id: UUID) -> None:
        """Delete a saved filter."""
        ...
