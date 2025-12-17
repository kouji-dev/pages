"""Get widget data use case."""

from typing import Any
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.dashboard import WidgetDataRequest, WidgetDataResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import IssueRepository, ProjectRepository
from src.domain.repositories.dashboard_repository import DashboardRepository
from src.infrastructure.database.models import IssueModel

logger = structlog.get_logger()


class GetWidgetDataUseCase:
    """Use case for getting widget data."""

    def __init__(
        self,
        dashboard_repository: DashboardRepository,
        issue_repository: IssueRepository,
        project_repository: ProjectRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies."""
        self._dashboard_repository = dashboard_repository
        self._issue_repository = issue_repository
        self._project_repository = project_repository
        self._session = session

    async def execute(
        self, dashboard_id: UUID, widget_id: UUID, request: WidgetDataRequest
    ) -> WidgetDataResponse:
        """Execute get widget data."""
        logger.info(
            "Getting widget data",
            dashboard_id=str(dashboard_id),
            widget_id=str(widget_id),
            widget_type=request.widget_type,
        )

        dashboard = await self._dashboard_repository.get_by_id(dashboard_id)
        if dashboard is None:
            raise EntityNotFoundException("Dashboard", str(dashboard_id))

        widget = next((w for w in dashboard.widgets if w.id == widget_id), None)
        if widget is None:
            raise EntityNotFoundException("DashboardWidget", str(widget_id))

        # Get project_id from dashboard or config
        project_id = dashboard.project_id
        if not project_id and request.config:
            project_id = request.config.get("project_id")

        if not project_id:
            raise EntityNotFoundException("Project", "No project specified")

        # Generate widget data based on type
        data: dict[str, Any] = {}

        if request.widget_type == "issue_status_breakdown":
            # Count issues by status
            result = await self._session.execute(
                select(
                    IssueModel.status,
                    func.count(IssueModel.id).label("count"),
                )
                .where(
                    IssueModel.project_id == project_id,
                    IssueModel.deleted_at.is_(None),
                )
                .group_by(IssueModel.status)
            )
            rows = result.all()
            data = {row.status: row.count for row in rows}

        elif request.widget_type == "issue_count_over_time":
            # Count issues created over time (last 30 days)
            from datetime import datetime, timedelta

            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)

            result = await self._session.execute(
                select(
                    func.date(IssueModel.created_at).label("date"),
                    func.count(IssueModel.id).label("count"),
                )
                .where(
                    IssueModel.project_id == project_id,
                    IssueModel.deleted_at.is_(None),
                    IssueModel.created_at >= start_date,
                    IssueModel.created_at <= end_date,
                )
                .group_by(func.date(IssueModel.created_at))
                .order_by(func.date(IssueModel.created_at))
            )
            rows = result.all()
            data = {str(row.date): row.count for row in rows}

        elif request.widget_type == "assigned_issues_list":
            # Get assigned issues (limit to 10)
            # Query issues directly from the session
            from sqlalchemy import select
            from src.infrastructure.database.models.issue import IssueModel

            stmt = select(IssueModel).where(
                IssueModel.project_id == project_id,
                IssueModel.assignee_id.is_not(None),
                IssueModel.deleted_at.is_(None),
            ).limit(10)
            result = await self._session.execute(stmt)
            issue_models = result.scalars().all()
            # Convert to dict format for widget data
            data = {
                "issues": [
                    {
                        "id": str(im.id),
                        "title": im.title,
                        "status": im.status,
                        "assignee_id": str(im.assignee_id) if im.assignee_id else None,
                    }
                    for im in issue_models
                ]
            }

        elif request.widget_type == "recent_activity_feed":
            # Get recent activity (placeholder - would need activity repository)
            data = {"activities": []}

        return WidgetDataResponse(data=data)
