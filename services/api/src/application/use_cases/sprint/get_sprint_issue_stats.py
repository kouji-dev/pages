"""Get sprint issue stats use case."""

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.sprint_stats import IssueStatsResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import IssueRepository, SprintRepository
from src.infrastructure.database.models import IssueModel

logger = structlog.get_logger()


class GetSprintIssueStatsUseCase:
    """Use case for getting sprint issue stats."""

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

    async def execute(self, sprint_id: UUID) -> IssueStatsResponse:
        """Execute getting sprint issue stats.

        Args:
            sprint_id: Sprint UUID

        Returns:
            Issue stats response DTO

        Raises:
            EntityNotFoundException: If sprint not found
        """
        logger.info("Getting sprint issue stats", sprint_id=str(sprint_id))

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
            return IssueStatsResponse(
                sprint_id=sprint_id,
                total_issues=0,
                completed_issues=0,
                in_progress_issues=0,
                todo_issues=0,
                cancelled_issues=0,
                total_story_points=0,
                completed_story_points=0,
                in_progress_story_points=0,
                todo_story_points=0,
            )

        # Get issues
        result = await self._session.execute(
            select(IssueModel)
            .where(IssueModel.id.in_(issue_ids))
            .where(IssueModel.deleted_at.is_(None))
        )
        issues = result.scalars().all()

        # Count issues by status
        completed_issues = 0
        in_progress_issues = 0
        todo_issues = 0
        cancelled_issues = 0

        # Count story points by status
        completed_story_points = 0
        in_progress_story_points = 0
        todo_story_points = 0

        for issue in issues:
            story_points = issue.story_points or 0

            if issue.status == "done":
                completed_issues += 1
                completed_story_points += story_points
            elif issue.status == "in_progress":
                in_progress_issues += 1
                in_progress_story_points += story_points
            elif issue.status == "todo":
                todo_issues += 1
                todo_story_points += story_points
            elif issue.status == "cancelled":
                cancelled_issues += 1

        total_issues = len(issues)
        total_story_points = sum(issue.story_points or 0 for issue in issues)

        return IssueStatsResponse(
            sprint_id=sprint_id,
            total_issues=total_issues,
            completed_issues=completed_issues,
            in_progress_issues=in_progress_issues,
            todo_issues=todo_issues,
            cancelled_issues=cancelled_issues,
            total_story_points=total_story_points,
            completed_story_points=completed_story_points,
            in_progress_story_points=in_progress_story_points,
            todo_story_points=todo_story_points,
        )

