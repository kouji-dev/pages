"""Update time entry use case."""

from uuid import UUID

import structlog

from src.application.dtos.time_entry import TimeEntryRequest, TimeEntryResponse
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories.time_entry_repository import TimeEntryRepository

logger = structlog.get_logger()


class UpdateTimeEntryUseCase:
    """Use case for updating a time entry."""

    def __init__(self, time_entry_repository: TimeEntryRepository) -> None:
        """Initialize use case with dependencies."""
        self._time_entry_repository = time_entry_repository

    async def execute(self, time_entry_id: UUID, request: TimeEntryRequest) -> TimeEntryResponse:
        """Execute update time entry."""
        logger.info("Updating time entry", entry_id=str(time_entry_id))

        time_entry = await self._time_entry_repository.get_by_id(time_entry_id)

        if time_entry is None:
            logger.warning("Time entry not found", entry_id=str(time_entry_id))
            raise EntityNotFoundException("TimeEntry", str(time_entry_id))

        # Apply updates
        if request.hours is not None:
            try:
                time_entry.update_hours(request.hours)
            except ValueError as e:
                raise ValidationException(str(e), field="hours") from e

        if request.date is not None:
            time_entry.update_date(request.date)

        if request.description is not None:
            time_entry.update_description(request.description)

        # Save to database
        updated_entry = await self._time_entry_repository.update(time_entry)

        logger.info("Time entry updated", entry_id=str(time_entry_id))

        return TimeEntryResponse.model_validate(
            {
                "id": updated_entry.id,
                "issue_id": updated_entry.issue_id,
                "user_id": updated_entry.user_id,
                "hours": updated_entry.hours,
                "date": updated_entry.date,
                "description": updated_entry.description,
                "created_at": updated_entry.created_at,
                "updated_at": updated_entry.updated_at,
            }
        )
