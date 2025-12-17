"""Get dashboard use case."""

from uuid import UUID

import structlog

from src.application.dtos.dashboard import DashboardResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.dashboard_repository import DashboardRepository

logger = structlog.get_logger()


class GetDashboardUseCase:
    """Use case for getting a dashboard."""

    def __init__(self, dashboard_repository: DashboardRepository) -> None:
        """Initialize use case with dependencies."""
        self._dashboard_repository = dashboard_repository

    async def execute(self, dashboard_id: UUID) -> DashboardResponse:
        """Execute get dashboard."""
        logger.info("Getting dashboard", dashboard_id=str(dashboard_id))

        dashboard = await self._dashboard_repository.get_by_id(dashboard_id)

        if dashboard is None:
            logger.warning("Dashboard not found", dashboard_id=str(dashboard_id))
            raise EntityNotFoundException("Dashboard", str(dashboard_id))

        return DashboardResponse.model_validate(
            {
                "id": dashboard.id,
                "project_id": dashboard.project_id,
                "user_id": dashboard.user_id,
                "name": dashboard.name,
                "layout": dashboard.layout,
                "created_at": dashboard.created_at,
                "updated_at": dashboard.updated_at,
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
                    for w in dashboard.widgets
                ],
            }
        )
