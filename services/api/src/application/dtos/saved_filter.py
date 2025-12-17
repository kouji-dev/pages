"""Saved filter DTOs."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CreateSavedFilterRequest(BaseModel):
    """Request DTO for creating a saved filter."""

    name: str = Field(..., min_length=1, max_length=100, description="Filter name")
    project_id: UUID | None = Field(default=None, description="Project ID (optional)")
    filter_criteria: dict[str, Any] = Field(..., description="Filter criteria dictionary")


class UpdateSavedFilterRequest(BaseModel):
    """Request DTO for updating a saved filter."""

    name: str | None = Field(default=None, min_length=1, max_length=100, description="Filter name")
    filter_criteria: dict[str, Any] | None = Field(
        default=None, description="Filter criteria dictionary"
    )


class SavedFilterResponse(BaseModel):
    """Response DTO for saved filter."""

    id: UUID
    user_id: UUID
    project_id: UUID | None
    name: str
    filter_criteria: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class SavedFilterListResponse(BaseModel):
    """Response DTO for saved filter list."""

    filters: list[SavedFilterResponse]
    total: int

    class Config:
        """Pydantic config."""

        from_attributes = True
