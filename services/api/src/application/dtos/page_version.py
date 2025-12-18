"""Page version DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PageVersionResponse(BaseModel):
    """Response DTO for page version data."""

    id: UUID
    page_id: UUID
    version_number: int
    title: str
    content: str | None = None
    created_by: UUID | None = None
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PageVersionListItemResponse(BaseModel):
    """Response DTO for page version in list view."""

    id: UUID
    page_id: UUID
    version_number: int
    title: str
    created_by: UUID | None = None
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PageVersionListResponse(BaseModel):
    """Response DTO for paginated page version list."""

    versions: list[PageVersionListItemResponse]
    total: int = Field(..., description="Total number of versions")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages_count: int = Field(..., description="Total number of pages (pagination)")


class PageVersionDiffResponse(BaseModel):
    """Response DTO for page version diff."""

    version_id: UUID
    compare_to_version_id: UUID | None = None
    version_number: int
    compare_to_version_number: int | None = None
    title_diff: dict[str, str | None] = Field(
        default_factory=dict, description="Title diff (old, new)"
    )
    content_diff: dict[str, str | None] = Field(
        default_factory=dict, description="Content diff (old, new)"
    )


class RestorePageVersionResponse(BaseModel):
    """Response DTO for restoring a page version."""

    page_id: UUID
    restored_version_id: UUID
    new_version_id: UUID
    message: str = Field(..., description="Success message")
