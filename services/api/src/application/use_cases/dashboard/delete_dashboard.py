"""Delete dashboard use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.dashboard_repository import DashboardRepository

logger = structlog.get_logger()


class DeleteDashboardUseCase:
    """Use case for deleting a dashboard."""

    def __init__(self, dashboard_repository: DashboardRepository) -> None:
        """Initialize use case with dependencies."""
        self._dashboard_repository = dashboard_repository

    async def execute(self, dashboard_id: UUID) -> None:
        """Execute delete dashboard."""
        logger.info("Deleting dashboard", dashboard_id=str(dashboard_id))

        dashboard = await self._dashboard_repository.get_by_id(dashboard_id)
        if dashboard is None:
            logger.warning("Dashboard not found", dashboard_id=str(dashboard_id))
            raise EntityNotFoundException("Dashboard", str(dashboard_id))

        await self._dashboard_repository.delete(dashboard_id)

        logger.info("Dashboard deleted", dashboard_id=str(dashboard_id))
