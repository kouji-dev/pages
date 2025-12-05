"""Organization DTOs."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class OrganizationResponse(BaseModel):
    """Response DTO for organization data."""

    id: UUID
    name: str
    slug: str
    description: str | None = None
    settings: dict[str, Any] | None = None
    member_count: int = Field(0, description="Number of members in the organization")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class OrganizationListItemResponse(BaseModel):
    """Response DTO for organization in list view."""

    id: UUID
    name: str
    slug: str
    description: str | None = None
    member_count: int = Field(0, description="Number of members in the organization")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class OrganizationListResponse(BaseModel):
    """Response DTO for paginated organization list."""

    organizations: list[OrganizationListItemResponse]
    total: int = Field(..., description="Total number of organizations")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class CreateOrganizationRequest(BaseModel):
    """Request DTO for creating an organization."""

    name: str = Field(..., min_length=1, max_length=100, description="Organization name")
    slug: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Organization slug (auto-generated from name if not provided)",
    )
    description: str | None = Field(None, max_length=1000, description="Organization description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and strip name."""
        return v.strip()

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str | None) -> str | None:
        """Validate and normalize slug."""
        if v is None:
            return None
        v = v.strip().lower()
        if not v:
            return None
        return v


class UpdateOrganizationRequest(BaseModel):
    """Request DTO for updating an organization."""

    name: str | None = Field(None, min_length=1, max_length=100, description="Organization name")
    slug: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Organization slug",
    )
    description: str | None = Field(None, max_length=1000, description="Organization description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate and strip name."""
        if v is None:
            return None
        return v.strip()

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str | None) -> str | None:
        """Validate and normalize slug."""
        if v is None:
            return None
        v = v.strip().lower()
        if not v:
            return None
        return v
