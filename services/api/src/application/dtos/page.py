"""Page DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class PageResponse(BaseModel):
    """Response DTO for page data."""

    id: UUID
    space_id: UUID
    title: str
    slug: str
    content: str | None = None
    parent_id: UUID | None = None
    created_by: UUID | None = None
    updated_by: UUID | None = None
    position: int = 0
    comment_count: int = Field(0, description="Number of comments on the page")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PageListItemResponse(BaseModel):
    """Response DTO for page in list view."""

    id: UUID
    space_id: UUID
    title: str
    slug: str
    parent_id: UUID | None = None
    created_by: UUID | None = None
    updated_by: UUID | None = None
    position: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PageListResponse(BaseModel):
    """Response DTO for paginated page list."""

    pages: list[PageListItemResponse]
    total: int = Field(..., description="Total number of pages")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages_count: int = Field(..., description="Total number of pages (pagination)")


class PageTreeItem(BaseModel):
    """Page tree item with children."""

    id: UUID
    space_id: UUID
    title: str
    slug: str
    content: str | None = None
    parent_id: UUID | None = None
    created_by: UUID | None = None
    updated_by: UUID | None = None
    position: int = 0
    children: list["PageTreeItem"] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# Forward reference resolution
PageTreeItem.model_rebuild()


class PageTreeResponse(BaseModel):
    """Response DTO for page tree structure."""

    pages: list[PageTreeItem]


class CreatePageRequest(BaseModel):
    """Request DTO for creating a page."""

    space_id: UUID = Field(..., description="ID of the space")
    title: str = Field(..., min_length=1, max_length=255, description="Page title")
    content: str | None = Field(None, description="Page content (rich text)")
    parent_id: UUID | None = Field(None, description="Parent page ID for hierarchy")
    slug: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Page slug (auto-generated from title if not provided)",
    )
    position: int = Field(0, ge=0, description="Position in the tree")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and strip title."""
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
        if len(v) > 255:
            raise ValueError("Page slug cannot exceed 255 characters")
        return v


class UpdatePageRequest(BaseModel):
    """Request DTO for updating a page."""

    title: str | None = Field(None, min_length=1, max_length=255, description="Page title")
    content: str | None = Field(None, description="Page content (rich text)")
    parent_id: UUID | None = Field(None, description="Parent page ID for hierarchy")
    slug: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Page slug",
    )
    position: int | None = Field(None, ge=0, description="Position in the tree")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """Validate and strip title."""
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
        if len(v) > 255:
            raise ValueError("Page slug cannot exceed 255 characters")
        return v
