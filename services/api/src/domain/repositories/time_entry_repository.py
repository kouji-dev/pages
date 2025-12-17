"""Time entry repository interface (port)."""

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from uuid import UUID

from src.domain.entities.time_entry import TimeEntry


class TimeEntryRepository(ABC):
    """Abstract time entry repository interface."""

    @abstractmethod
    async def create(self, time_entry: TimeEntry) -> TimeEntry:
        """Create a new time entry."""
        ...

    @abstractmethod
    async def get_by_id(self, time_entry_id: UUID) -> TimeEntry | None:
        """Get time entry by ID."""
        ...

    @abstractmethod
    async def get_by_issue_id(self, issue_id: UUID) -> list[TimeEntry]:
        """Get all time entries for an issue."""
        ...

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list[TimeEntry]:
        """Get all time entries for a user."""
        ...

    @abstractmethod
    async def get_by_issue_and_date_range(
        self, issue_id: UUID, start_date: date, end_date: date
    ) -> list[TimeEntry]:
        """Get time entries for an issue within a date range."""
        ...

    @abstractmethod
    async def get_total_hours_by_issue(self, issue_id: UUID) -> Decimal:
        """Get total hours logged for an issue."""
        ...

    @abstractmethod
    async def get_total_hours_by_user(self, user_id: UUID) -> Decimal:
        """Get total hours logged by a user."""
        ...

    @abstractmethod
    async def update(self, time_entry: TimeEntry) -> TimeEntry:
        """Update an existing time entry."""
        ...

    @abstractmethod
    async def delete(self, time_entry_id: UUID) -> None:
        """Delete a time entry."""
        ...
