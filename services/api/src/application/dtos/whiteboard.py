"""Whiteboard DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WhiteboardResponse(BaseModel):
    """Response DTO for whiteboard data."""

    id: UUID
    space_id: UUID
    name: str
    data: str | None = None
    created_by: UUID | None = None
    updated_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class WhiteboardListItemResponse(BaseModel):
    """Response DTO for whiteboard in list view."""

    id: UUID
    space_id: UUID
    name: str
    created_by: UUID | None = None
    updated_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class WhiteboardListResponse(BaseModel):
    """Response DTO for paginated whiteboard list."""

    whiteboards: list[WhiteboardListItemResponse]
    total: int = Field(..., description="Total number of whiteboards")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages_count: int = Field(..., description="Total number of pages (pagination)")


class CreateWhiteboardRequest(BaseModel):
    """Request DTO for creating a whiteboard."""

    space_id: UUID = Field(..., description="ID of the space")
    name: str = Field(..., min_length=1, max_length=100, description="Whiteboard name")
    data: str | None = Field(None, description="Initial whiteboard data (JSON)")


class UpdateWhiteboardRequest(BaseModel):
    """Request DTO for updating a whiteboard."""

    name: str | None = Field(None, min_length=1, max_length=100, description="Whiteboard name")
    data: str | None = Field(None, description="Whiteboard data (JSON)")
