"""Dashboard DTOs."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class DashboardWidgetRequest(BaseModel):
    """Request DTO for creating/updating a dashboard widget."""

    type: str = Field(..., description="Widget type")
    config: dict[str, Any] | None = Field(default=None, description="Widget configuration")
    position: int = Field(default=0, ge=0, description="Widget position")


class DashboardWidgetResponse(BaseModel):
    """Response DTO for dashboard widget."""

    id: UUID
    dashboard_id: UUID
    type: str
    config: dict[str, Any] | None
    position: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class CreateDashboardRequest(BaseModel):
    """Request DTO for creating a dashboard."""

    name: str = Field(..., min_length=1, max_length=100, description="Dashboard name")
    project_id: UUID | None = Field(default=None, description="Project ID (optional)")
    layout: dict[str, Any] | None = Field(default=None, description="Dashboard layout")
    widgets: list[DashboardWidgetRequest] = Field(
        default_factory=list, description="Initial widgets"
    )


class UpdateDashboardRequest(BaseModel):
    """Request DTO for updating a dashboard."""

    name: str | None = Field(
        default=None, min_length=1, max_length=100, description="Dashboard name"
    )
    layout: dict[str, Any] | None = Field(default=None, description="Dashboard layout")


class DashboardResponse(BaseModel):
    """Response DTO for dashboard."""

    id: UUID
    project_id: UUID | None
    user_id: UUID | None
    name: str
    layout: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
    widgets: list[DashboardWidgetResponse] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        from_attributes = True


class DashboardListResponse(BaseModel):
    """Response DTO for dashboard list."""

    dashboards: list[DashboardResponse]
    total: int

    class Config:
        """Pydantic config."""

        from_attributes = True


class WidgetDataRequest(BaseModel):
    """Request DTO for widget data."""

    widget_type: str = Field(..., description="Widget type")
    config: dict[str, Any] | None = Field(default=None, description="Widget configuration")


class WidgetDataResponse(BaseModel):
    """Response DTO for widget data."""

    data: dict[str, Any] = Field(..., description="Widget data")

    class Config:
        """Pydantic config."""

        from_attributes = True
