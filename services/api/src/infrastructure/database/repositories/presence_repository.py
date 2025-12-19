"""SQLAlchemy implementation of PresenceRepository."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Presence
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PresenceRepository
from src.infrastructure.database.models import PresenceModel


class SQLAlchemyPresenceRepository(PresenceRepository):
    """SQLAlchemy implementation of PresenceRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, presence: Presence) -> Presence:
        """Create a new presence in the database."""
        model = PresenceModel(
            id=presence.id,
            page_id=presence.page_id,
            user_id=presence.user_id,
            cursor_position=presence.cursor_position,
            selection=presence.selection,
            socket_id=presence.socket_id,
            created_at=presence.created_at,
            updated_at=presence.updated_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_page_and_user(self, page_id: UUID, user_id: UUID) -> Presence | None:
        """Get presence by page ID and user ID."""
        result = await self._session.execute(
            select(PresenceModel).where(
                PresenceModel.page_id == page_id,
                PresenceModel.user_id == user_id,
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_all_by_page(self, page_id: UUID) -> list[Presence]:
        """Get all presences for a page."""
        result = await self._session.execute(
            select(PresenceModel).where(PresenceModel.page_id == page_id)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def update(self, presence: Presence) -> Presence:
        """Update an existing presence."""
        result = await self._session.execute(
            select(PresenceModel).where(PresenceModel.id == presence.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Presence", str(presence.id))

        model.cursor_position = presence.cursor_position
        model.selection = presence.selection
        model.socket_id = presence.socket_id
        model.updated_at = presence.updated_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, presence_id: UUID) -> None:
        """Delete a presence."""
        result = await self._session.execute(
            select(PresenceModel).where(PresenceModel.id == presence_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Presence", str(presence_id))

        await self._session.delete(model)
        await self._session.flush()

    async def delete_by_page_and_user(self, page_id: UUID, user_id: UUID) -> None:
        """Delete presence by page ID and user ID."""
        await self._session.execute(
            delete(PresenceModel).where(
                PresenceModel.page_id == page_id,
                PresenceModel.user_id == user_id,
            )
        )
        await self._session.flush()

    async def delete_by_socket_id(self, socket_id: str) -> None:
        """Delete all presences for a socket ID."""
        await self._session.execute(
            delete(PresenceModel).where(PresenceModel.socket_id == socket_id)
        )
        await self._session.flush()

    def _to_entity(self, model: PresenceModel) -> Presence:
        """Convert database model to domain entity."""
        return Presence(
            id=model.id,
            page_id=model.page_id,
            user_id=model.user_id,
            cursor_position=model.cursor_position,
            selection=model.selection,
            socket_id=model.socket_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
