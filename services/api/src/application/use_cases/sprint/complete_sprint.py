"""Complete sprint use case."""

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.sprint_metrics import CompleteSprintRequest, CompleteSprintResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import IssueRepository, SprintRepository
from src.domain.value_objects.sprint_status import SprintStatus
from src.infrastructure.database.models import IssueModel

logger = structlog.get_logger()


class CompleteSprintUseCase:
    """Use case for completing a sprint."""

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

    async def execute(
        self,
        sprint_id: UUID,
        request: CompleteSprintRequest,
    ) -> CompleteSprintResponse:
        """Execute sprint completion.

        Args:
            sprint_id: Sprint UUID
            request: Complete sprint request

        Returns:
            Complete sprint response with metrics

        Raises:
            EntityNotFoundException: If sprint not found
        """
        logger.info("Completing sprint", sprint_id=str(sprint_id))

        # Verify sprint exists
        sprint = await self._sprint_repository.get_by_id(sprint_id)
        if sprint is None:
            logger.warning("Sprint not found", sprint_id=str(sprint_id))
            raise EntityNotFoundException("Sprint", str(sprint_id))

        # Get sprint issues
        sprint_issues = await self._sprint_repository.get_sprint_issues(sprint_id)
        issue_ids = [issue_id for issue_id, _ in sprint_issues]

        incomplete_issues_moved = 0

        if issue_ids:
            # Get issues
            result = await self._session.execute(
                select(IssueModel)
                .where(IssueModel.id.in_(issue_ids))
                .where(IssueModel.deleted_at.is_(None))
            )
            issues = result.scalars().all()

            # Move incomplete issues to backlog if requested
            if request.move_incomplete_to_backlog:
                for issue in issues:
                    if issue.status not in ("done", "cancelled"):
                        # Remove from sprint
                        await self._sprint_repository.remove_issue_from_sprint(sprint_id, issue.id)
                        # Clear backlog_order to move to end of backlog
                        issue.backlog_order = None
                        await self._session.flush()
                        incomplete_issues_moved += 1

        # Update sprint status to completed
        sprint.update_status(SprintStatus.COMPLETED)
        await self._sprint_repository.update(sprint)

        # Get final metrics
        from src.application.use_cases.sprint.get_sprint_metrics import (
            GetSprintMetricsUseCase,
        )

        metrics_use_case = GetSprintMetricsUseCase(
            self._sprint_repository, self._issue_repository, self._session
        )
        metrics = await metrics_use_case.execute(sprint_id)

        logger.info(
            "Sprint completed successfully",
            sprint_id=str(sprint_id),
            incomplete_issues_moved=incomplete_issues_moved,
        )

        return CompleteSprintResponse(
            sprint_id=sprint_id,
            incomplete_issues_moved=incomplete_issues_moved,
            metrics=metrics,
        )
