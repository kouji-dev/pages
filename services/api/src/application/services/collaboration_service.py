"""Real-time collaboration service."""

from uuid import UUID

import structlog

from src.domain.entities import Presence
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageRepository, PresenceRepository, UserRepository

logger = structlog.get_logger()


class CollaborationService:
    """Service for managing real-time collaboration."""

    def __init__(
        self,
        presence_repository: PresenceRepository,
        page_repository: PageRepository,
        user_repository: UserRepository,
    ) -> None:
        """Initialize collaboration service with dependencies.

        Args:
            presence_repository: Presence repository
            page_repository: Page repository
            user_repository: User repository
        """
        self._presence_repository = presence_repository
        self._page_repository = page_repository
        self._user_repository = user_repository

    async def join_page(
        self,
        page_id: UUID,
        user_id: UUID,
        socket_id: str,
    ) -> Presence:
        """Join a page for real-time collaboration.

        Args:
            page_id: Page UUID
            user_id: User UUID
            socket_id: WebSocket connection ID

        Returns:
            Created or updated presence

        Raises:
            EntityNotFoundException: If page or user not found
        """
        logger.info("User joining page", page_id=str(page_id), user_id=str(user_id))

        # Verify page exists
        page = await self._page_repository.get_by_id(page_id)
        if page is None:
            raise EntityNotFoundException("Page", str(page_id))

        # Verify user exists
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise EntityNotFoundException("User", str(user_id))

        # Get or create presence
        presence = await self._presence_repository.get_by_page_and_user(page_id, user_id)

        if presence:
            presence.update_socket_id(socket_id)
            return await self._presence_repository.update(presence)
        else:
            presence = Presence.create(
                page_id=page_id,
                user_id=user_id,
                socket_id=socket_id,
            )
            return await self._presence_repository.create(presence)

    async def leave_page(
        self,
        page_id: UUID,
        user_id: UUID,
    ) -> None:
        """Leave a page (remove presence).

        Args:
            page_id: Page UUID
            user_id: User UUID
        """
        logger.info("User leaving page", page_id=str(page_id), user_id=str(user_id))

        await self._presence_repository.delete_by_page_and_user(page_id, user_id)

    async def update_cursor(
        self,
        page_id: UUID,
        user_id: UUID,
        cursor_position: str | None,
    ) -> Presence:
        """Update user cursor position on a page.

        Args:
            page_id: Page UUID
            user_id: User UUID
            cursor_position: JSON cursor position data

        Returns:
            Updated presence

        Raises:
            EntityNotFoundException: If presence not found
        """
        presence = await self._presence_repository.get_by_page_and_user(page_id, user_id)

        if presence is None:
            raise EntityNotFoundException("Presence", f"{page_id}:{user_id}")

        presence.update_cursor(cursor_position)
        return await self._presence_repository.update(presence)

    async def update_selection(
        self,
        page_id: UUID,
        user_id: UUID,
        selection: str | None,
    ) -> Presence:
        """Update user selection on a page.

        Args:
            page_id: Page UUID
            user_id: User UUID
            selection: JSON selection data

        Returns:
            Updated presence

        Raises:
            EntityNotFoundException: If presence not found
        """
        presence = await self._presence_repository.get_by_page_and_user(page_id, user_id)

        if presence is None:
            raise EntityNotFoundException("Presence", f"{page_id}:{user_id}")

        presence.update_selection(selection)
        return await self._presence_repository.update(presence)

    async def get_page_presences(self, page_id: UUID) -> list[Presence]:
        """Get all active presences for a page.

        Args:
            page_id: Page UUID

        Returns:
            List of presences
        """
        return await self._presence_repository.get_all_by_page(page_id)

    async def disconnect_socket(self, socket_id: str) -> None:
        """Handle socket disconnection.

        Args:
            socket_id: WebSocket connection ID
        """
        logger.info("Socket disconnecting", socket_id=socket_id)
        await self._presence_repository.delete_by_socket_id(socket_id)
