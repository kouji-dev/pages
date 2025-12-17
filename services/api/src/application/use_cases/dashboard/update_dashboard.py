"""Update dashboard use case."""

from uuid import UUID

import structlog

from src.application.dtos.dashboard import DashboardResponse, UpdateDashboardRequest
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.dashboard_repository import DashboardRepository

logger = structlog.get_logger()


class UpdateDashboardUseCase:
    """Use case for updating a dashboard."""

    def __init__(self, dashboard_repository: DashboardRepository) -> None:
        """Initialize use case with dependencies."""
        self._dashboard_repository = dashboard_repository

    async def execute(
        self, dashboard_id: UUID, request: UpdateDashboardRequest
    ) -> DashboardResponse:
        """Execute update dashboard."""
        logger.info("Updating dashboard", dashboard_id=str(dashboard_id))

        dashboard = await self._dashboard_repository.get_by_id(dashboard_id)

        if dashboard is None:
            logger.warning("Dashboard not found", dashboard_id=str(dashboard_id))
            raise EntityNotFoundException("Dashboard", str(dashboard_id))

        # Apply updates
        if request.name is not None:
            dashboard.name = request.name
            dashboard._touch()

        if request.layout is not None:
            dashboard.layout = request.layout
            dashboard._touch()

        # Save to database
        updated_dashboard = await self._dashboard_repository.update(dashboard)

        logger.info("Dashboard updated", dashboard_id=str(dashboard_id))

        return DashboardResponse.model_validate(
            {
                "id": updated_dashboard.id,
                "project_id": updated_dashboard.project_id,
                "user_id": updated_dashboard.user_id,
                "name": updated_dashboard.name,
                "layout": updated_dashboard.layout,
                "created_at": updated_dashboard.created_at,
                "updated_at": updated_dashboard.updated_at,
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
                    for w in updated_dashboard.widgets
                ],
            }
        )
