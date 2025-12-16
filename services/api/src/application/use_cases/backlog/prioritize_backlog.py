"""Prioritize backlog use case."""

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.backlog import PrioritizeBacklogRequest
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import ProjectRepository
from src.infrastructure.database.models import IssueModel

logger = structlog.get_logger()


class PrioritizeBacklogUseCase:
    """Use case for prioritizing backlog issues."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            project_repository: Project repository to verify project exists
            session: Database session for queries
        """
        self._project_repository = project_repository
        self._session = session

    async def execute(
        self,
        project_id: UUID,
        request: PrioritizeBacklogRequest,
    ) -> None:
        """Execute backlog prioritization.

        Args:
            project_id: Project UUID
            request: Prioritize backlog request

        Raises:
            EntityNotFoundException: If project not found
        """
        logger.info(
            "Prioritizing backlog",
            project_id=str(project_id),
            issue_count=len(request.issue_ids),
        )

        # Verify project exists
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            logger.warning("Project not found", project_id=str(project_id))
            raise EntityNotFoundException("Project", str(project_id))

        # Update backlog_order for each issue
        for order, issue_id in enumerate(request.issue_ids):
            result = await self._session.execute(
                select(IssueModel).where(
                    IssueModel.id == issue_id,
                    IssueModel.project_id == project_id,
                    IssueModel.deleted_at.is_(None),
                )
            )
            issue = result.scalar_one_or_none()

            if issue:
                issue.backlog_order = order
            else:
                logger.warning(
                    "Issue not found or doesn't belong to project",
                    issue_id=str(issue_id),
                    project_id=str(project_id),
                )

        await self._session.flush()

        logger.info("Backlog prioritized successfully", project_id=str(project_id))
