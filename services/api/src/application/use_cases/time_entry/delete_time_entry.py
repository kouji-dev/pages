"""Delete time entry use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.time_entry_repository import TimeEntryRepository

logger = structlog.get_logger()


class DeleteTimeEntryUseCase:
    """Use case for deleting a time entry."""

    def __init__(self, time_entry_repository: TimeEntryRepository) -> None:
        """Initialize use case with dependencies."""
        self._time_entry_repository = time_entry_repository

    async def execute(self, time_entry_id: UUID) -> None:
        """Execute delete time entry."""
        logger.info("Deleting time entry", entry_id=str(time_entry_id))

        time_entry = await self._time_entry_repository.get_by_id(time_entry_id)
        if time_entry is None:
            logger.warning("Time entry not found", entry_id=str(time_entry_id))
            raise EntityNotFoundException("TimeEntry", str(time_entry_id))

        await self._time_entry_repository.delete(time_entry_id)

        logger.info("Time entry deleted", entry_id=str(time_entry_id))
