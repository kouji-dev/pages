"""Backlog DTOs."""

from uuid import UUID

from pydantic import BaseModel, Field


class BacklogListResponse(BaseModel):
    """Response DTO for paginated backlog list."""

    issues: list[UUID] = Field(..., description="List of issue IDs in backlog order")
    total: int = Field(..., description="Total number of issues in backlog")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class PrioritizeBacklogRequest(BaseModel):
    """Request DTO for prioritizing backlog."""

    issue_ids: list[UUID] = Field(
        ...,
        description="List of issue IDs in priority order (first = highest priority)",
    )


class ReorderBacklogIssueRequest(BaseModel):
    """Request DTO for reordering a single issue in backlog."""

    position: int = Field(
        ...,
        ge=0,
        description="New position in backlog (0 = highest priority)",
    )
