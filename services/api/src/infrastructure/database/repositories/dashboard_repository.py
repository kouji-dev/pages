"""SQLAlchemy implementation of DashboardRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.dashboard import Dashboard, DashboardWidget
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.dashboard_repository import DashboardRepository
from src.infrastructure.database.models.dashboard import (
    DashboardModel,
    DashboardWidgetModel,
)


class SQLAlchemyDashboardRepository(DashboardRepository):
    """SQLAlchemy implementation of DashboardRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    async def create(self, dashboard: Dashboard) -> Dashboard:
        """Create a new dashboard in the database."""
        dashboard_model = DashboardModel(
            id=dashboard.id,
            project_id=dashboard.project_id,
            user_id=dashboard.user_id,
            name=dashboard.name,
            layout=dashboard.layout,
            created_at=dashboard.created_at,
            updated_at=dashboard.updated_at,
        )

        self._session.add(dashboard_model)

        # Create widget models
        for widget in dashboard.widgets:
            widget_model = DashboardWidgetModel(
                id=widget.id,
                dashboard_id=widget.dashboard_id,
                type=widget.type,
                config=widget.config,
                position=widget.position,
                created_at=widget.created_at,
                updated_at=widget.updated_at,
            )
            self._session.add(widget_model)

        await self._session.flush()
        await self._session.refresh(dashboard_model)

        reloaded = await self._get_by_id(dashboard.id)
        if reloaded is None:
            raise RuntimeError("Failed to reload created dashboard")
        return reloaded

    async def get_by_id(self, dashboard_id: UUID) -> Dashboard | None:
        """Get dashboard by ID."""
        return await self._get_by_id(dashboard_id)

    async def _get_by_id(self, dashboard_id: UUID) -> Dashboard | None:
        """Internal method to get dashboard by ID with relationships."""
        result = await self._session.execute(
            select(DashboardModel).where(DashboardModel.id == dashboard_id)
        )
        dashboard_model = result.scalar_one_or_none()

        if dashboard_model is None:
            return None

        return self._to_entity(dashboard_model)

    async def get_by_project_id(self, project_id: UUID) -> list[Dashboard]:
        """Get all dashboards for a project."""
        result = await self._session.execute(
            select(DashboardModel).where(DashboardModel.project_id == project_id)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_by_user_id(self, user_id: UUID) -> list[Dashboard]:
        """Get all dashboards for a user."""
        result = await self._session.execute(
            select(DashboardModel).where(DashboardModel.user_id == user_id)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def update(self, dashboard: Dashboard) -> Dashboard:
        """Update an existing dashboard."""
        result = await self._session.execute(
            select(DashboardModel).where(DashboardModel.id == dashboard.id)
        )
        dashboard_model = result.scalar_one_or_none()

        if dashboard_model is None:
            raise EntityNotFoundException("Dashboard", str(dashboard.id))

        dashboard_model.name = dashboard.name
        dashboard_model.layout = dashboard.layout
        dashboard_model.updated_at = dashboard.updated_at

        # Update widgets
        existing_widget_ids = {w.id for w in dashboard_model.widgets}
        new_widget_ids = {w.id for w in dashboard.widgets}

        # Delete removed widgets
        widgets_to_delete = [w for w in dashboard_model.widgets if w.id not in new_widget_ids]
        for widget_model in widgets_to_delete:
            await self._session.delete(widget_model)

        # Update or create widgets
        for widget in dashboard.widgets:
            if widget.id in existing_widget_ids:
                widget_model = next((w for w in dashboard_model.widgets if w.id == widget.id), None)
                if widget_model:
                    widget_model.type = widget.type
                    widget_model.config = widget.config
                    widget_model.position = widget.position
                    widget_model.updated_at = widget.updated_at
            else:
                widget_model = DashboardWidgetModel(
                    id=widget.id,
                    dashboard_id=widget.dashboard_id,
                    type=widget.type,
                    config=widget.config,
                    position=widget.position,
                    created_at=widget.created_at,
                    updated_at=widget.updated_at,
                )
                self._session.add(widget_model)

        await self._session.flush()
        await self._session.refresh(dashboard_model)

        updated = await self._get_by_id(dashboard.id)
        if updated is None:
            raise ValueError(f"Dashboard {dashboard.id} not found after update")
        return updated

    async def delete(self, dashboard_id: UUID) -> None:
        """Delete a dashboard."""
        result = await self._session.execute(
            select(DashboardModel).where(DashboardModel.id == dashboard_id)
        )
        dashboard_model = result.scalar_one_or_none()

        if dashboard_model is None:
            raise EntityNotFoundException("Dashboard", str(dashboard_id))

        await self._session.delete(dashboard_model)
        await self._session.flush()

    def _to_entity(self, model: DashboardModel) -> Dashboard:
        """Convert DashboardModel to Dashboard entity."""
        widgets = [
            DashboardWidget(
                id=w.id,
                dashboard_id=w.dashboard_id,
                type=w.type,
                config=w.config,
                position=w.position,
                created_at=w.created_at,
                updated_at=w.updated_at,
            )
            for w in model.widgets
        ]

        return Dashboard(
            id=model.id,
            project_id=model.project_id,
            user_id=model.user_id,
            name=model.name,
            layout=model.layout,
            created_at=model.created_at,
            updated_at=model.updated_at,
            widgets=widgets,
        )
