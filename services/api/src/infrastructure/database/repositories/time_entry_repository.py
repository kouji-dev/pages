"""SQLAlchemy implementation of TimeEntryRepository."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.time_entry import TimeEntry
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.time_entry_repository import TimeEntryRepository
from src.infrastructure.database.models.time_entry import TimeEntryModel


class SQLAlchemyTimeEntryRepository(TimeEntryRepository):
    """SQLAlchemy implementation of TimeEntryRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    async def create(self, time_entry: TimeEntry) -> TimeEntry:
        """Create a new time entry in the database."""
        model = TimeEntryModel(
            id=time_entry.id,
            issue_id=time_entry.issue_id,
            user_id=time_entry.user_id,
            hours=time_entry.hours,
            date=time_entry.date,
            description=time_entry.description,
            created_at=time_entry.created_at,
            updated_at=time_entry.updated_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, time_entry_id: UUID) -> TimeEntry | None:
        """Get time entry by ID."""
        result = await self._session.execute(
            select(TimeEntryModel).where(TimeEntryModel.id == time_entry_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_issue_id(self, issue_id: UUID) -> list[TimeEntry]:
        """Get all time entries for an issue."""
        result = await self._session.execute(
            select(TimeEntryModel).where(TimeEntryModel.issue_id == issue_id)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_by_user_id(self, user_id: UUID) -> list[TimeEntry]:
        """Get all time entries for a user."""
        result = await self._session.execute(
            select(TimeEntryModel).where(TimeEntryModel.user_id == user_id)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_by_issue_and_date_range(
        self, issue_id: UUID, start_date: date, end_date: date
    ) -> list[TimeEntry]:
        """Get time entries for an issue within a date range."""
        result = await self._session.execute(
            select(TimeEntryModel).where(
                TimeEntryModel.issue_id == issue_id,
                TimeEntryModel.date >= start_date,
                TimeEntryModel.date <= end_date,
            )
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_total_hours_by_issue(self, issue_id: UUID) -> Decimal:
        """Get total hours logged for an issue."""
        result = await self._session.execute(
            select(func.coalesce(func.sum(TimeEntryModel.hours), 0)).where(
                TimeEntryModel.issue_id == issue_id
            )
        )
        total = result.scalar_one() or Decimal("0")
        return Decimal(str(total))

    async def get_total_hours_by_user(self, user_id: UUID) -> Decimal:
        """Get total hours logged by a user."""
        result = await self._session.execute(
            select(func.coalesce(func.sum(TimeEntryModel.hours), 0)).where(
                TimeEntryModel.user_id == user_id
            )
        )
        total = result.scalar_one() or Decimal("0")
        return Decimal(str(total))

    async def update(self, time_entry: TimeEntry) -> TimeEntry:
        """Update an existing time entry."""
        result = await self._session.execute(
            select(TimeEntryModel).where(TimeEntryModel.id == time_entry.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("TimeEntry", str(time_entry.id))

        model.hours = time_entry.hours
        model.date = time_entry.date
        model.description = time_entry.description
        model.updated_at = time_entry.updated_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, time_entry_id: UUID) -> None:
        """Delete a time entry."""
        result = await self._session.execute(
            select(TimeEntryModel).where(TimeEntryModel.id == time_entry_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("TimeEntry", str(time_entry_id))

        await self._session.delete(model)
        await self._session.flush()

    def _to_entity(self, model: TimeEntryModel) -> TimeEntry:
        """Convert TimeEntryModel to TimeEntry entity."""
        return TimeEntry(
            id=model.id,
            issue_id=model.issue_id,
            user_id=model.user_id,
            hours=model.hours,
            date=model.date,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
