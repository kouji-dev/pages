"""Template DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TemplateResponse(BaseModel):
    """Response DTO for template data."""

    id: UUID
    organization_id: UUID
    name: str
    description: str | None = None
    content: str | None = None
    is_default: bool = False
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class TemplateListItemResponse(BaseModel):
    """Response DTO for template in list view."""

    id: UUID
    organization_id: UUID
    name: str
    description: str | None = None
    is_default: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class TemplateListResponse(BaseModel):
    """Response DTO for paginated template list."""

    templates: list[TemplateListItemResponse]
    total: int = Field(..., description="Total number of templates")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class CreateTemplateRequest(BaseModel):
    """Request DTO for creating a template."""

    organization_id: UUID = Field(..., description="ID of the organization")
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: str | None = Field(None, max_length=500, description="Template description")
    content: str | None = Field(None, description="Template content (HTML or Markdown)")
    is_default: bool = Field(False, description="Whether this is a default template")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and strip name."""
        return v.strip()


class UpdateTemplateRequest(BaseModel):
    """Request DTO for updating a template."""

    name: str | None = Field(None, min_length=1, max_length=100, description="Template name")
    description: str | None = Field(None, max_length=500, description="Template description")
    content: str | None = Field(None, description="Template content (HTML or Markdown)")
    is_default: bool | None = Field(None, description="Whether this is a default template")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate and strip name."""
        if v is None:
            return None
        return v.strip()
