"""SQLAlchemy implementation of WhiteboardRepository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Whiteboard
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import WhiteboardRepository
from src.infrastructure.database.models import WhiteboardModel


class SQLAlchemyWhiteboardRepository(WhiteboardRepository):
    """SQLAlchemy implementation of WhiteboardRepository.

    Adapts the domain WhiteboardRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, whiteboard: Whiteboard) -> Whiteboard:
        """Create a new whiteboard in the database."""
        model = WhiteboardModel(
            id=whiteboard.id,
            space_id=whiteboard.space_id,
            name=whiteboard.name,
            data=whiteboard.data,
            created_by=whiteboard.created_by,
            updated_by=whiteboard.updated_by,
            created_at=whiteboard.created_at,
            updated_at=whiteboard.updated_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, whiteboard_id: UUID) -> Whiteboard | None:
        """Get whiteboard by ID."""
        result = await self._session.execute(
            select(WhiteboardModel).where(WhiteboardModel.id == whiteboard_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_all(
        self,
        space_id: UUID,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
    ) -> list[Whiteboard]:
        """Get all whiteboards in a space with pagination."""
        query = select(WhiteboardModel).where(WhiteboardModel.space_id == space_id)

        query = query.offset(skip).limit(limit).order_by(WhiteboardModel.created_at.desc())

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count(
        self,
        space_id: UUID,
        include_deleted: bool = False,
    ) -> int:
        """Count total whiteboards in a space."""
        query = select(func.count(WhiteboardModel.id)).where(WhiteboardModel.space_id == space_id)

        result = await self._session.execute(query)
        return result.scalar_one() or 0

    async def update(self, whiteboard: Whiteboard) -> Whiteboard:
        """Update an existing whiteboard."""
        result = await self._session.execute(
            select(WhiteboardModel).where(WhiteboardModel.id == whiteboard.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Whiteboard", str(whiteboard.id))

        model.name = whiteboard.name
        model.data = whiteboard.data
        model.updated_by = whiteboard.updated_by
        model.updated_at = whiteboard.updated_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, whiteboard_id: UUID) -> None:
        """Hard delete a whiteboard."""
        result = await self._session.execute(
            select(WhiteboardModel).where(WhiteboardModel.id == whiteboard_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Whiteboard", str(whiteboard_id))

        await self._session.delete(model)
        await self._session.flush()

    def _to_entity(self, model: WhiteboardModel) -> Whiteboard:
        """Convert database model to domain entity."""
        return Whiteboard(
            id=model.id,
            space_id=model.space_id,
            name=model.name,
            data=model.data,
            created_by=model.created_by,
            updated_by=model.updated_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
