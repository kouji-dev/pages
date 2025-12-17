"""Dashboard repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.dashboard import Dashboard


class DashboardRepository(ABC):
    """Abstract dashboard repository interface."""

    @abstractmethod
    async def create(self, dashboard: Dashboard) -> Dashboard:
        """Create a new dashboard."""
        ...

    @abstractmethod
    async def get_by_id(self, dashboard_id: UUID) -> Dashboard | None:
        """Get dashboard by ID."""
        ...

    @abstractmethod
    async def get_by_project_id(self, project_id: UUID) -> list[Dashboard]:
        """Get all dashboards for a project."""
        ...

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list[Dashboard]:
        """Get all dashboards for a user."""
        ...

    @abstractmethod
    async def update(self, dashboard: Dashboard) -> Dashboard:
        """Update an existing dashboard."""
        ...

    @abstractmethod
    async def delete(self, dashboard_id: UUID) -> None:
        """Delete a dashboard."""
        ...
