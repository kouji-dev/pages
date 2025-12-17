"""Dashboard domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Self
from uuid import UUID, uuid4


@dataclass
class DashboardWidget:
    """Dashboard widget entity."""

    id: UUID
    dashboard_id: UUID
    type: str
    config: dict[str, Any] | None = None
    position: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    VALID_WIDGET_TYPES = {
        "issue_status_breakdown",
        "issue_count_over_time",
        "assigned_issues_list",
        "recent_activity_feed",
    }

    def __post_init__(self) -> None:
        """Validate widget."""
        if self.type not in self.VALID_WIDGET_TYPES:
            raise ValueError(f"Widget type must be one of: {', '.join(self.VALID_WIDGET_TYPES)}")

    @classmethod
    def create(
        cls,
        dashboard_id: UUID,
        type: str,
        config: dict[str, Any] | None = None,
        position: int = 0,
    ) -> Self:
        """Create a new dashboard widget."""
        if type not in cls.VALID_WIDGET_TYPES:
            raise ValueError(f"Widget type must be one of: {', '.join(cls.VALID_WIDGET_TYPES)}")

        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            dashboard_id=dashboard_id,
            type=type,
            config=config,
            position=position,
            created_at=now,
            updated_at=now,
        )

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


@dataclass
class Dashboard:
    """Dashboard domain entity."""

    id: UUID
    project_id: UUID | None
    user_id: UUID | None
    name: str
    layout: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Aggregated entities
    widgets: list[DashboardWidget] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate dashboard."""
        if not self.name or not self.name.strip():
            raise ValueError("Dashboard name cannot be empty")

        self.name = self.name.strip()

        if len(self.name) > 100:
            raise ValueError("Dashboard name cannot exceed 100 characters")

    @classmethod
    def create(
        cls,
        project_id: UUID | None,
        user_id: UUID | None,
        name: str,
        layout: dict[str, Any] | None = None,
    ) -> Self:
        """Create a new dashboard."""
        if not project_id and not user_id:
            raise ValueError("Dashboard must have either project_id or user_id")

        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            project_id=project_id,
            user_id=user_id,
            name=name,
            layout=layout,
            created_at=now,
            updated_at=now,
            widgets=[],
        )

    def add_widget(
        self,
        type: str,
        config: dict[str, Any] | None = None,
        position: int | None = None,
    ) -> DashboardWidget:
        """Add a widget to this dashboard."""
        if position is None:
            position = len(self.widgets)

        widget = DashboardWidget.create(
            dashboard_id=self.id,
            type=type,
            config=config,
            position=position,
        )
        self.widgets.append(widget)
        self._touch()
        return widget

    def remove_widget(self, widget_id: UUID) -> None:
        """Remove a widget from this dashboard."""
        widget = next((w for w in self.widgets if w.id == widget_id), None)
        if widget is None:
            raise ValueError(f"Widget {widget_id} not found in dashboard")

        self.widgets.remove(widget)
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
