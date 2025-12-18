"""Presence DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PresenceResponse(BaseModel):
    """Response DTO for presence data."""

    id: UUID
    page_id: UUID
    user_id: UUID
    cursor_position: str | None = None
    selection: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PresenceListResponse(BaseModel):
    """Response DTO for presence list."""

    presences: list[PresenceResponse]
    total: int = Field(..., description="Total number of active presences")


class UpdateCursorRequest(BaseModel):
    """Request DTO for updating cursor position."""

    cursor_position: str | None = Field(None, description="JSON cursor position data")


class UpdateSelectionRequest(BaseModel):
    """Request DTO for updating selection."""

    selection: str | None = Field(None, description="JSON selection data")
