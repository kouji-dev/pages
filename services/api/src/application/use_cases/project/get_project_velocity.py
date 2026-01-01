"""Get project velocity report use case."""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.project_reports import (
    VelocityDataPoint,
    VelocityReportResponse,
)
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import ProjectRepository, SprintRepository
from src.infrastructure.database.models import IssueModel, SprintIssueModel, SprintModel

logger = structlog.get_logger()


class GetProjectVelocityUseCase:
    """Use case for getting project velocity report."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        sprint_repository: SprintRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            project_repository: Project repository
            sprint_repository: Sprint repository
            session: Database session
        """
        self._project_repository = project_repository
        self._sprint_repository = sprint_repository
        self._session = session

    async def execute(self, project_id: UUID) -> VelocityReportResponse:
        """Execute getting project velocity report.

        Args:
            project_id: Project UUID

        Returns:
            Velocity report response DTO

        Raises:
            EntityNotFoundException: If project not found
        """
        logger.info("Getting project velocity report", project_id=str(project_id))

        # Verify project exists
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            logger.warning("Project not found", project_id=str(project_id))
            raise EntityNotFoundException("Project", str(project_id))

        # Get all completed and active sprints for the project
        sprints_result = await self._session.execute(
            select(SprintModel)
            .where(SprintModel.project_id == project_id)
            .where(SprintModel.status.in_(["completed", "active"]))
            .order_by(SprintModel.start_date.asc())
        )
        sprints = sprints_result.scalars().all()

        velocity_data: list[VelocityDataPoint] = []

        for sprint in sprints:
            # Get sprint issues
            sprint_issues_result = await self._session.execute(
                select(SprintIssueModel.issue_id)
                .where(SprintIssueModel.sprint_id == sprint.id)
            )
            issue_ids = [row[0] for row in sprint_issues_result.all()]

            if not issue_ids:
                # No issues in sprint
                velocity_data.append(
                    VelocityDataPoint(
                        sprint_id=sprint.id,
                        sprint_name=sprint.name,
                        committed=0,
                        completed=0,
                    )
                )
                continue

            # Get committed story points (all issues in sprint)
            committed_result = await self._session.execute(
                select(func.coalesce(func.sum(IssueModel.story_points), 0))
                .where(IssueModel.id.in_(issue_ids))
                .where(IssueModel.deleted_at.is_(None))
            )
            committed = int(committed_result.scalar_one() or 0)

            # Get completed story points (only done issues)
            completed_result = await self._session.execute(
                select(func.coalesce(func.sum(IssueModel.story_points), 0))
                .where(IssueModel.id.in_(issue_ids))
                .where(IssueModel.status == "done")
                .where(IssueModel.deleted_at.is_(None))
            )
            completed = int(completed_result.scalar_one() or 0)

            velocity_data.append(
                VelocityDataPoint(
                    sprint_id=sprint.id,
                    sprint_name=sprint.name,
                    committed=committed,
                    completed=completed,
                )
            )

        return VelocityReportResponse(
            project_id=project_id,
            velocity_data=velocity_data,
        )
