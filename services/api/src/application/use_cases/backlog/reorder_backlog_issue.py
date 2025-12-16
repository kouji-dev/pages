"""Reorder single backlog issue use case."""

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.backlog import ReorderBacklogIssueRequest
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import ProjectRepository, SprintRepository
from src.infrastructure.database.models import IssueModel, SprintIssueModel

logger = structlog.get_logger()


class ReorderBacklogIssueUseCase:
    """Use case for reordering a single issue in backlog."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        sprint_repository: SprintRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            project_repository: Project repository to verify project exists
            sprint_repository: Sprint repository to verify issue is not in sprint
            session: Database session for queries
        """
        self._project_repository = project_repository
        self._sprint_repository = sprint_repository
        self._session = session

    async def execute(
        self,
        project_id: UUID,
        issue_id: UUID,
        request: ReorderBacklogIssueRequest,
    ) -> None:
        """Execute reordering a single backlog issue.

        Args:
            project_id: Project UUID
            issue_id: Issue UUID
            request: Reorder backlog issue request

        Raises:
            EntityNotFoundException: If project or issue not found
        """
        logger.info(
            "Reordering backlog issue",
            project_id=str(project_id),
            issue_id=str(issue_id),
            position=request.position,
        )

        # Verify project exists
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            logger.warning("Project not found", project_id=str(project_id))
            raise EntityNotFoundException("Project", str(project_id))

        # Verify issue exists and belongs to project
        result = await self._session.execute(
            select(IssueModel).where(
                IssueModel.id == issue_id,
                IssueModel.project_id == project_id,
                IssueModel.deleted_at.is_(None),
            )
        )
        issue = result.scalar_one_or_none()

        if issue is None:
            logger.warning("Issue not found", issue_id=str(issue_id))
            raise EntityNotFoundException("Issue", str(issue_id))

        # Verify issue is not in a sprint
        sprint = await self._sprint_repository.get_issue_sprint(issue_id)
        if sprint is not None:
            logger.warning(
                "Issue is in a sprint, cannot reorder in backlog",
                issue_id=str(issue_id),
                sprint_id=str(sprint.id),
            )
            raise EntityNotFoundException("BacklogIssue", str(issue_id))

        # Get all backlog issues (not in sprints) for this project
        sprint_issues_result = await self._session.execute(
            select(SprintIssueModel.issue_id).distinct()
        )
        sprint_issue_ids = {row[0] for row in sprint_issues_result.all()}

        backlog_query = select(IssueModel).where(
            IssueModel.project_id == project_id,
            IssueModel.deleted_at.is_(None),
        )

        if sprint_issue_ids:
            backlog_query = backlog_query.where(~IssueModel.id.in_(sprint_issue_ids))

        backlog_result = await self._session.execute(backlog_query)
        backlog_issues = backlog_result.scalars().all()

        # Remove the issue being reordered from the list
        backlog_issues = [i for i in backlog_issues if i.id != issue_id]

        # Sort by current backlog_order
        backlog_issues.sort(
            key=lambda x: (
                x.backlog_order if x.backlog_order is not None else float("inf"),
                x.created_at,
            )
        )

        # Insert issue at new position
        new_position = min(request.position, len(backlog_issues))
        backlog_issues.insert(new_position, issue)

        # Update backlog_order for all issues
        for order, backlog_issue in enumerate(backlog_issues):
            backlog_issue.backlog_order = order

        await self._session.flush()

        logger.info(
            "Backlog issue reordered successfully",
            project_id=str(project_id),
            issue_id=str(issue_id),
        )
