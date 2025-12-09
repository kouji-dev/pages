"""Search DTOs for issues and pages."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    """Unified search result item."""

    entity_type: Literal["issue", "page"] = Field(
        ..., description="Type of the entity returned by the search"
    )
    id: UUID
    title: str
    snippet: str | None = Field(
        None,
        description="Optional snippet or preview extracted from content/description",
    )
    score: float = Field(..., description="Relevance score returned by the search")
    project_id: UUID | None = Field(None, description="Project ID for issue results")
    space_id: UUID | None = Field(None, description="Space ID for page results")


class SearchResponse(BaseModel):
    """Unified search response with pagination."""

    items: list[SearchResultItem]
    total: int
    page: int
    limit: int


class SearchIssuesResponse(SearchResponse):
    """Search issues response."""


class SearchPagesResponse(SearchResponse):
    """Search pages response."""
