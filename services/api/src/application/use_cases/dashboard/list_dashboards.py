"""List dashboards use case."""

from uuid import UUID

import structlog

from src.application.dtos.dashboard import DashboardListResponse, DashboardResponse
from src.domain.repositories.dashboard_repository import DashboardRepository

logger = structlog.get_logger()


class ListDashboardsUseCase:
    """Use case for listing dashboards."""

    def __init__(self, dashboard_repository: DashboardRepository) -> None:
        """Initialize use case with dependencies."""
        self._dashboard_repository = dashboard_repository

    async def execute(self, user_id: UUID, project_id: UUID | None = None) -> DashboardListResponse:
        """Execute list dashboards."""
        logger.info("Listing dashboards", user_id=str(user_id), project_id=str(project_id))

        if project_id:
            dashboards = await self._dashboard_repository.get_by_project_id(project_id)
        else:
            dashboards = await self._dashboard_repository.get_by_user_id(user_id)

        dashboard_items = [
            DashboardResponse.model_validate(
                {
                    "id": d.id,
                    "project_id": d.project_id,
                    "user_id": d.user_id,
                    "name": d.name,
                    "layout": d.layout,
                    "created_at": d.created_at,
                    "updated_at": d.updated_at,
                    "widgets": [
                        {
                            "id": w.id,
                            "dashboard_id": w.dashboard_id,
                            "type": w.type,
                            "config": w.config,
                            "position": w.position,
                            "created_at": w.created_at,
                            "updated_at": w.updated_at,
                        }
                        for w in d.widgets
                    ],
                }
            )
            for d in dashboards
        ]

        return DashboardListResponse(dashboards=dashboard_items, total=len(dashboard_items))
