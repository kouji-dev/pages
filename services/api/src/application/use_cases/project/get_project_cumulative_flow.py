"""Get project cumulative flow report use case."""

from datetime import date, datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.project_reports import (
    CumulativeFlowDataPoint,
    CumulativeFlowReportResponse,
)
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import ProjectRepository
from src.infrastructure.database.models import IssueModel

logger = structlog.get_logger()


class GetProjectCumulativeFlowUseCase:
    """Use case for getting project cumulative flow report."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            project_repository: Project repository
            session: Database session
        """
        self._project_repository = project_repository
        self._session = session

    async def execute(
        self, project_id: UUID, days: int = 7
    ) -> CumulativeFlowReportResponse:
        """Execute getting project cumulative flow report.

        Args:
            project_id: Project UUID
            days: Number of days to include (default: 7, last week)

        Returns:
            Cumulative flow report response DTO

        Raises:
            EntityNotFoundException: If project not found
        """
        logger.info(
            "Getting project cumulative flow report",
            project_id=str(project_id),
            days=days,
        )

        # Verify project exists
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            logger.warning("Project not found", project_id=str(project_id))
            raise EntityNotFoundException("Project", str(project_id))

        # Calculate date range (last N days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        # Get all issues in the project
        issues_result = await self._session.execute(
            select(IssueModel)
            .where(IssueModel.project_id == project_id)
            .where(IssueModel.deleted_at.is_(None))
        )
        issues = issues_result.scalars().all()

        # Group issues by status for each day
        flow_data: list[CumulativeFlowDataPoint] = []
        current_date = start_date

        while current_date <= end_date:
            # Count issues by status as of this date
            # For simplicity, we use current status (in a real implementation,
            # you'd track status changes over time)
            todo_count = sum(
                1
                for issue in issues
                if issue.status == "todo"
                and (not issue.created_at or issue.created_at.date() <= current_date)
            )
            in_progress_count = sum(
                1
                for issue in issues
                if issue.status == "in_progress"
                and (not issue.created_at or issue.created_at.date() <= current_date)
            )
            done_count = sum(
                1
                for issue in issues
                if issue.status == "done"
                and (not issue.created_at or issue.created_at.date() <= current_date)
            )

            flow_data.append(
                CumulativeFlowDataPoint(
                    date=current_date,
                    todo=todo_count,
                    in_progress=in_progress_count,
                    done=done_count,
                )
            )

            current_date += timedelta(days=1)

        return CumulativeFlowReportResponse(
            project_id=project_id,
            flow_data=flow_data,
        )
