"""Get sprint metrics use case."""

from datetime import date, timedelta
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.sprint_metrics import BurndownDataPoint, SprintMetricsResponse
from src.domain.entities import Sprint
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import IssueRepository, SprintRepository
from src.infrastructure.database.models import IssueModel

logger = structlog.get_logger()


class GetSprintMetricsUseCase:
    """Use case for getting sprint metrics."""

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

    async def execute(self, sprint_id: UUID) -> SprintMetricsResponse:
        """Execute getting sprint metrics.

        Args:
            sprint_id: Sprint UUID

        Returns:
            Sprint metrics response DTO

        Raises:
            EntityNotFoundException: If sprint not found
        """
        logger.info("Getting sprint metrics", sprint_id=str(sprint_id))

        # Verify sprint exists
        sprint = await self._sprint_repository.get_by_id(sprint_id)
        if sprint is None:
            logger.warning("Sprint not found", sprint_id=str(sprint_id))
            raise EntityNotFoundException("Sprint", str(sprint_id))

        # Get sprint issues
        sprint_issues = await self._sprint_repository.get_sprint_issues(sprint_id)
        issue_ids = [issue_id for issue_id, _ in sprint_issues]

        if not issue_ids:
            # No issues in sprint
            return SprintMetricsResponse(
                sprint_id=sprint_id,
                total_story_points=0,
                completed_story_points=0,
                remaining_story_points=0,
                completion_percentage=0.0,
                velocity=0.0,
                issue_counts={},
                burndown_data=[],
            )

        # Get issues with story points
        result = await self._session.execute(
            select(IssueModel)
            .where(IssueModel.id.in_(issue_ids))
            .where(IssueModel.deleted_at.is_(None))
        )
        issues = result.scalars().all()

        # Calculate metrics
        total_story_points = sum(issue.story_points or 0 for issue in issues)
        completed_story_points = sum(
            issue.story_points or 0 for issue in issues if issue.status == "done"
        )
        remaining_story_points = total_story_points - completed_story_points

        completion_percentage = (
            (completed_story_points / total_story_points * 100) if total_story_points > 0 else 0.0
        )

        velocity = float(completed_story_points)

        # Count issues by status
        issue_counts: dict[str, int] = {}
        for issue in issues:
            issue_counts[issue.status] = issue_counts.get(issue.status, 0) + 1

        # Generate burndown data
        burndown_data = await self._generate_burndown_data(sprint, list(issues))

        return SprintMetricsResponse(
            sprint_id=sprint_id,
            total_story_points=total_story_points,
            completed_story_points=completed_story_points,
            remaining_story_points=remaining_story_points,
            completion_percentage=completion_percentage,
            velocity=velocity,
            issue_counts=issue_counts,
            burndown_data=burndown_data,
        )

    async def _generate_burndown_data(
        self, sprint: Sprint, issues: list[IssueModel]
    ) -> list[BurndownDataPoint]:
        """Generate burndown chart data points.

        Args:
            sprint: Sprint entity
            issues: List of issues in sprint

        Returns:
            List of burndown data points
        """
        if not sprint.start_date or not sprint.end_date:
            return []

        total_story_points = sum(issue.story_points or 0 for issue in issues)
        if total_story_points == 0:
            return []

        # Calculate daily ideal burn rate
        days = (sprint.end_date - sprint.start_date).days + 1
        daily_burn = total_story_points / days if days > 0 else 0

        burndown_data: list[BurndownDataPoint] = []
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
                BurndownDataPoint(
                    point_date=current_date,
                    ideal=round(ideal_remaining, 2),
                    actual=round(actual_remaining, 2),
                )
            )

            current_date += timedelta(days=1)

        return burndown_data
