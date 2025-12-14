"""Space DTOs."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.application.dtos.page import PageListItemResponse


class SpaceResponse(BaseModel):
    """Response DTO for space data."""

    id: UUID
    organization_id: UUID
    name: str
    key: str
    description: str | None = None
    settings: dict[str, Any] | None = None
    page_count: int = Field(0, description="Number of pages in the space")
    recent_pages: list[PageListItemResponse] = Field(
        default_factory=list, description="Recent pages in the space (up to 5)"
    )
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class SpaceListItemResponse(BaseModel):
    """Response DTO for space in list view."""

    id: UUID
    organization_id: UUID
    name: str
    key: str
    description: str | None = None
    page_count: int = Field(0, description="Number of pages in the space")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class SpaceListResponse(BaseModel):
    """Response DTO for paginated space list."""

    spaces: list[SpaceListItemResponse]
    total: int = Field(..., description="Total number of spaces")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class CreateSpaceRequest(BaseModel):
    """Request DTO for creating a space."""

    organization_id: UUID = Field(..., description="ID of the organization")
    name: str = Field(..., min_length=1, max_length=100, description="Space name")
    key: str | None = Field(
        None,
        min_length=1,
        max_length=10,
        description="Space key (auto-generated from name if not provided)",
    )
    description: str | None = Field(None, max_length=1000, description="Space description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and strip name."""
        return v.strip()

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str | None) -> str | None:
        """Validate and normalize key."""
        if v is None:
            return None
        v = v.strip().upper()
        if not v:
            return None
        if len(v) > 10:
            raise ValueError("Space key cannot exceed 10 characters")
        return v


class UpdateSpaceRequest(BaseModel):
    """Request DTO for updating a space."""

    name: str | None = Field(None, min_length=1, max_length=100, description="Space name")
    key: str | None = Field(
        None,
        min_length=1,
        max_length=10,
        description="Space key",
    )
    description: str | None = Field(None, max_length=1000, description="Space description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate and strip name."""
        if v is None:
            return None
        return v.strip()

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str | None) -> str | None:
        """Validate and normalize key."""
        if v is None:
            return None
        v = v.strip().upper()
        if not v:
            return None
        if len(v) > 10:
            raise ValueError("Space key cannot exceed 10 characters")
        return v
