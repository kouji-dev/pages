"""Create dashboard use case."""

from uuid import UUID

import structlog

from src.application.dtos.dashboard import CreateDashboardRequest, DashboardResponse
from src.domain.entities.dashboard import Dashboard
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import ProjectRepository
from src.domain.repositories.dashboard_repository import DashboardRepository

logger = structlog.get_logger()


class CreateDashboardUseCase:
    """Use case for creating a dashboard."""

    def __init__(
        self,
        dashboard_repository: DashboardRepository,
        project_repository: ProjectRepository | None = None,
    ) -> None:
        """Initialize use case with dependencies."""
        self._dashboard_repository = dashboard_repository
        self._project_repository = project_repository

    async def execute(self, user_id: UUID, request: CreateDashboardRequest) -> DashboardResponse:
        """Execute create dashboard."""
        logger.info("Creating dashboard", user_id=str(user_id), name=request.name)

        # Verify project exists if provided
        if request.project_id:
            if self._project_repository is None:
                raise ValidationException("Project repository not available", field="project_id")
            project = await self._project_repository.get_by_id(request.project_id)
            if project is None:
                logger.warning("Project not found", project_id=str(request.project_id))
                raise EntityNotFoundException("Project", str(request.project_id))

        # Create dashboard entity
        try:
            dashboard = Dashboard.create(
                project_id=request.project_id,
                user_id=user_id,
                name=request.name,
                layout=request.layout,
            )
        except ValueError as e:
            raise ValidationException(str(e), field="dashboard") from e

        # Add widgets
        for widget_req in request.widgets:
            try:
                dashboard.add_widget(
                    type=widget_req.type,
                    config=widget_req.config,
                    position=widget_req.position,
                )
            except ValueError as e:
                raise ValidationException(str(e), field="widgets") from e

        # Save to database
        created_dashboard = await self._dashboard_repository.create(dashboard)

        logger.info("Dashboard created", dashboard_id=str(created_dashboard.id))

        return DashboardResponse.model_validate(
            {
                "id": created_dashboard.id,
                "project_id": created_dashboard.project_id,
                "user_id": created_dashboard.user_id,
                "name": created_dashboard.name,
                "layout": created_dashboard.layout,
                "created_at": created_dashboard.created_at,
                "updated_at": created_dashboard.updated_at,
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
                    for w in created_dashboard.widgets
                ],
            }
        )
