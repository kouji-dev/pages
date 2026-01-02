"""Get sprint burndown stats use case."""

from datetime import date, timedelta
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.sprint_stats import BurndownStatsResponse
from src.domain.entities import Sprint
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import IssueRepository, SprintRepository
from src.infrastructure.database.models import IssueModel

logger = structlog.get_logger()


class GetSprintBurndownStatsUseCase:
    """Use case for getting sprint burndown stats."""

    def __init__(
        self,
        sprint_repository: SprintRepository,
        issue_repository: IssueRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            sprint_repository: Sprint repository
            issue_repository: Issue repository
            session: Database session for queries
        """
        self._sprint_repository = sprint_repository
        self._issue_repository = issue_repository
        self._session = session

    async def execute(self, sprint_id: UUID) -> BurndownStatsResponse:
        """Execute getting sprint burndown stats.

        Args:
            sprint_id: Sprint UUID

        Returns:
            Burndown stats response DTO

        Raises:
            EntityNotFoundException: If sprint not found
        """
        logger.info("Getting sprint burndown stats", sprint_id=str(sprint_id))

        # Verify sprint exists
        sprint = await self._sprint_repository.get_by_id(sprint_id)
        if sprint is None:
            logger.warning("Sprint not found", sprint_id=str(sprint_id))
            raise EntityNotFoundException("Sprint", str(sprint_id))

        # Get sprint issues
        sprint_issues = await self._sprint_repository.get_sprint_issues(sprint_id)
        issue_ids = [issue_id for issue_id, _ in sprint_issues]

        if not issue_ids or not sprint.start_date or not sprint.end_date:
            # No issues or no dates
            return BurndownStatsResponse(
                sprint_id=sprint_id,
                burndown_data=[],
            )

        # Get issues with story points
        result = await self._session.execute(
            select(IssueModel)
            .where(IssueModel.id.in_(issue_ids))
            .where(IssueModel.deleted_at.is_(None))
        )
        issues = result.scalars().all()

        # Calculate total story points
        total_story_points = sum(issue.story_points or 0 for issue in issues)
        if total_story_points == 0:
            return BurndownStatsResponse(
                sprint_id=sprint_id,
                burndown_data=[],
            )

        # Calculate daily ideal burn rate
        days = (sprint.end_date - sprint.start_date).days + 1
        daily_burn = total_story_points / days if days > 0 else 0

        burndown_data: list[dict[str, float | str]] = []
        current_date = sprint.start_date
        completed_by_date: dict[date, int] = {}

        # Track completed story points by date (simplified - using issue updated_at)
        for issue in issues:
            if issue.status == "done" and issue.updated_at:
                issue_date = issue.updated_at.date()
                completed_by_date[issue_date] = completed_by_date.get(issue_date, 0) + (
                    issue.story_points or 0
                )

        cumulative_completed = 0
        while current_date <= sprint.end_date:
            # Update cumulative completed
            cumulative_completed += completed_by_date.get(current_date, 0)

            ideal_remaining = max(
                0, total_story_points - (daily_burn * (current_date - sprint.start_date).days)
            )
            actual_remaining = max(0, total_story_points - cumulative_completed)

            burndown_data.append(
                {
                    "date": current_date.isoformat(),
                    "ideal": round(ideal_remaining, 2),
                    "actual": round(actual_remaining, 2),
                }
            )

            current_date += timedelta(days=1)

        return BurndownStatsResponse(
            sprint_id=sprint_id,
            burndown_data=burndown_data,
        )

