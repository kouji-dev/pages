"""Get time summary use case."""

from uuid import UUID

import structlog

from src.application.dtos.time_entry import TimeSummaryResponse
from src.domain.repositories.time_entry_repository import TimeEntryRepository

logger = structlog.get_logger()


class GetTimeSummaryUseCase:
    """Use case for getting time tracking summary."""

    def __init__(self, time_entry_repository: TimeEntryRepository) -> None:
        """Initialize use case with dependencies."""
        self._time_entry_repository = time_entry_repository

    async def execute(self, issue_id: UUID) -> TimeSummaryResponse:
        """Execute get time summary."""
        logger.info("Getting time summary", issue_id=str(issue_id))

        # Get total hours
        total_hours = await self._time_entry_repository.get_total_hours_by_issue(issue_id)

        # Get all entries for the issue
        entries = await self._time_entry_repository.get_by_issue_id(issue_id)

        # Calculate hours by user
        hours_by_user: dict[str, float] = {}
        for entry in entries:
            user_id_str = str(entry.user_id)
            if user_id_str not in hours_by_user:
                hours_by_user[user_id_str] = 0
            hours_by_user[user_id_str] += float(entry.hours)

        # Calculate hours by date
        hours_by_date: dict[str, float] = {}
        for entry in entries:
            date_str = entry.date.isoformat()
            if date_str not in hours_by_date:
                hours_by_date[date_str] = 0
            hours_by_date[date_str] += float(entry.hours)

        return TimeSummaryResponse(
            total_hours=total_hours,
            hours_by_user={k: float(v) for k, v in hours_by_user.items()},
            hours_by_date_range={k: float(v) for k, v in hours_by_date.items()},
        )
