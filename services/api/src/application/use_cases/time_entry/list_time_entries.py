"""List time entries use case."""

from uuid import UUID

import structlog

from src.application.dtos.time_entry import TimeEntryListResponse, TimeEntryResponse
from src.domain.repositories.time_entry_repository import TimeEntryRepository

logger = structlog.get_logger()


class ListTimeEntriesUseCase:
    """Use case for listing time entries."""

    def __init__(self, time_entry_repository: TimeEntryRepository) -> None:
        """Initialize use case with dependencies."""
        self._time_entry_repository = time_entry_repository

    async def execute(self, issue_id: UUID) -> TimeEntryListResponse:
        """Execute list time entries."""
        logger.info("Listing time entries", issue_id=str(issue_id))

        entries = await self._time_entry_repository.get_by_issue_id(issue_id)

        entry_items = [
            TimeEntryResponse.model_validate(
                {
                    "id": e.id,
                    "issue_id": e.issue_id,
                    "user_id": e.user_id,
                    "hours": e.hours,
                    "date": e.date,
                    "description": e.description,
                    "created_at": e.created_at,
                    "updated_at": e.updated_at,
                }
            )
            for e in entries
        ]

        return TimeEntryListResponse(entries=entry_items, total=len(entry_items))
