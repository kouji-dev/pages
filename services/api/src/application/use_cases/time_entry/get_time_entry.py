"""Get time entry use case."""

from uuid import UUID

import structlog

from src.application.dtos.time_entry import TimeEntryResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.time_entry_repository import TimeEntryRepository

logger = structlog.get_logger()


class GetTimeEntryUseCase:
    """Use case for getting a time entry."""

    def __init__(self, time_entry_repository: TimeEntryRepository) -> None:
        """Initialize use case with dependencies."""
        self._time_entry_repository = time_entry_repository

    async def execute(self, time_entry_id: UUID) -> TimeEntryResponse:
        """Execute get time entry."""
        logger.info("Getting time entry", entry_id=str(time_entry_id))

        time_entry = await self._time_entry_repository.get_by_id(time_entry_id)

        if time_entry is None:
            logger.warning("Time entry not found", entry_id=str(time_entry_id))
            raise EntityNotFoundException("TimeEntry", str(time_entry_id))

        return TimeEntryResponse.model_validate(
            {
                "id": time_entry.id,
                "issue_id": time_entry.issue_id,
                "user_id": time_entry.user_id,
                "hours": time_entry.hours,
                "date": time_entry.date,
                "description": time_entry.description,
                "created_at": time_entry.created_at,
                "updated_at": time_entry.updated_at,
            }
        )
