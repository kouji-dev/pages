"""Label DTOs."""

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


def validate_hex_color(v: str) -> str:
    """Validate hex color (#RGB or #RRGGBB)."""
    if not v or not v.strip():
        raise ValueError("Color cannot be empty")
    v = v.strip().lower()
    if not v.startswith("#"):
        v = "#" + v
    if not re.match(r"^#[0-9a-f]{3}([0-9a-f]{3})?$", v):
        raise ValueError("Color must be a valid hex code (#RGB or #RRGGBB)")
    return v


class LabelResponse(BaseModel):
    """Response DTO for label data."""

    id: UUID
    project_id: UUID
    name: str
    color: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class LabelListResponse(BaseModel):
    """Response DTO for paginated label list."""

    labels: list[LabelResponse]
    total: int = Field(..., description="Total number of labels")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class CreateLabelRequest(BaseModel):
    """Request DTO for creating a label."""

    name: str = Field(..., min_length=1, max_length=100, description="Label name")
    color: str = Field(..., description="Hex color (#RGB or #RRGGBB)")
    description: str | None = Field(None, max_length=2000, description="Label description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and strip name."""
        v = v.strip()
        if not v:
            raise ValueError("Label name cannot be empty")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate hex color."""
        return validate_hex_color(v)


class UpdateLabelRequest(BaseModel):
    """Request DTO for updating a label."""

    name: str | None = Field(None, min_length=1, max_length=100, description="Label name")
    color: str | None = Field(None, description="Hex color (#RGB or #RRGGBB)")
    description: str | None = Field(None, max_length=2000, description="Label description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate and strip name."""
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("Label name cannot be empty")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        """Validate hex color."""
        if v is None:
            return None
        return validate_hex_color(v)


class AddLabelToIssueRequest(BaseModel):
    """Request DTO for adding a label to an issue."""

    label_id: UUID = Field(..., description="Label ID to add")
