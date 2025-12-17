"""SQLAlchemy implementation of SavedFilterRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.saved_filter import SavedFilter
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.saved_filter_repository import SavedFilterRepository
from src.infrastructure.database.models.saved_filter import SavedFilterModel


class SQLAlchemySavedFilterRepository(SavedFilterRepository):
    """SQLAlchemy implementation of SavedFilterRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    async def create(self, saved_filter: SavedFilter) -> SavedFilter:
        """Create a new saved filter in the database."""
        model = SavedFilterModel(
            id=saved_filter.id,
            user_id=saved_filter.user_id,
            project_id=saved_filter.project_id,
            name=saved_filter.name,
            filter_criteria=saved_filter.filter_criteria,
            created_at=saved_filter.created_at,
            updated_at=saved_filter.updated_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, filter_id: UUID) -> SavedFilter | None:
        """Get saved filter by ID."""
        result = await self._session.execute(
            select(SavedFilterModel).where(SavedFilterModel.id == filter_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_user_id(self, user_id: UUID) -> list[SavedFilter]:
        """Get all saved filters for a user."""
        result = await self._session.execute(
            select(SavedFilterModel).where(SavedFilterModel.user_id == user_id)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_by_user_and_project(self, user_id: UUID, project_id: UUID) -> list[SavedFilter]:
        """Get all saved filters for a user in a project."""
        result = await self._session.execute(
            select(SavedFilterModel).where(
                SavedFilterModel.user_id == user_id,
                SavedFilterModel.project_id == project_id,
            )
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def update(self, saved_filter: SavedFilter) -> SavedFilter:
        """Update an existing saved filter."""
        result = await self._session.execute(
            select(SavedFilterModel).where(SavedFilterModel.id == saved_filter.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("SavedFilter", str(saved_filter.id))

        model.name = saved_filter.name
        model.filter_criteria = saved_filter.filter_criteria
        model.updated_at = saved_filter.updated_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, filter_id: UUID) -> None:
        """Delete a saved filter."""
        result = await self._session.execute(
            select(SavedFilterModel).where(SavedFilterModel.id == filter_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("SavedFilter", str(filter_id))

        await self._session.delete(model)
        await self._session.flush()

    def _to_entity(self, model: SavedFilterModel) -> SavedFilter:
        """Convert SavedFilterModel to SavedFilter entity."""
        return SavedFilter(
            id=model.id,
            user_id=model.user_id,
            project_id=model.project_id,
            name=model.name,
            filter_criteria=model.filter_criteria,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
