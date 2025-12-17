"""Create time entry use case."""

from uuid import UUID

import structlog

from src.application.dtos.time_entry import TimeEntryRequest, TimeEntryResponse
from src.domain.entities.time_entry import TimeEntry
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import IssueRepository
from src.domain.repositories.time_entry_repository import TimeEntryRepository

logger = structlog.get_logger()


class CreateTimeEntryUseCase:
    """Use case for creating a time entry."""

    def __init__(
        self,
        time_entry_repository: TimeEntryRepository,
        issue_repository: IssueRepository,
    ) -> None:
        """Initialize use case with dependencies."""
        self._time_entry_repository = time_entry_repository
        self._issue_repository = issue_repository

    async def execute(
        self, issue_id: UUID, user_id: UUID, request: TimeEntryRequest
    ) -> TimeEntryResponse:
        """Execute create time entry."""
        logger.info("Creating time entry", issue_id=str(issue_id), user_id=str(user_id))

        # Verify issue exists
        issue = await self._issue_repository.get_by_id(issue_id)
        if issue is None:
            logger.warning("Issue not found", issue_id=str(issue_id))
            raise EntityNotFoundException("Issue", str(issue_id))

        # Create time entry entity
        try:
            time_entry = TimeEntry.create(
                issue_id=issue_id,
                user_id=user_id,
                hours=request.hours,
                date=request.date,
                description=request.description,
            )
        except ValueError as e:
            raise ValidationException(str(e), field="hours") from e

        # Save to database
        created_entry = await self._time_entry_repository.create(time_entry)

        logger.info("Time entry created", entry_id=str(created_entry.id))

        return TimeEntryResponse.model_validate(
            {
                "id": created_entry.id,
                "issue_id": created_entry.issue_id,
                "user_id": created_entry.user_id,
                "hours": created_entry.hours,
                "date": created_entry.date,
                "description": created_entry.description,
                "created_at": created_entry.created_at,
                "updated_at": created_entry.updated_at,
            }
        )
