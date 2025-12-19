"""Presence repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Presence


class PresenceRepository(ABC):
    """Abstract presence repository interface."""

    @abstractmethod
    async def create(self, presence: Presence) -> Presence:
        """Create a new presence.

        Args:
            presence: Presence entity to create

        Returns:
            Created presence with persisted data
        """
        ...

    @abstractmethod
    async def get_by_page_and_user(self, page_id: UUID, user_id: UUID) -> Presence | None:
        """Get presence by page ID and user ID.

        Args:
            page_id: Page UUID
            user_id: User UUID

        Returns:
            Presence if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_all_by_page(self, page_id: UUID) -> list[Presence]:
        """Get all presences for a page.

        Args:
            page_id: Page UUID

        Returns:
            List of presences
        """
        ...

    @abstractmethod
    async def update(self, presence: Presence) -> Presence:
        """Update an existing presence.

        Args:
            presence: Presence entity with updated data

        Returns:
            Updated presence

        Raises:
            EntityNotFoundException: If presence not found
        """
        ...

    @abstractmethod
    async def delete(self, presence_id: UUID) -> None:
        """Delete a presence.

        Args:
            presence_id: Presence UUID

        Raises:
            EntityNotFoundException: If presence not found
        """
        ...

    @abstractmethod
    async def delete_by_page_and_user(self, page_id: UUID, user_id: UUID) -> None:
        """Delete presence by page ID and user ID.

        Args:
            page_id: Page UUID
            user_id: User UUID
        """
        ...

    @abstractmethod
    async def delete_by_socket_id(self, socket_id: str) -> None:
        """Delete all presences for a socket ID.

        Args:
            socket_id: Socket ID
        """
        ...
