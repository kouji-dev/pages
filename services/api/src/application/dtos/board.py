"""Board DTOs."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class BoardListColumnResponse(BaseModel):
    """Response DTO for a board list (column)."""

    id: UUID
    board_id: UUID
    list_type: str = Field(..., description="label, assignee, or milestone")
    list_config: dict[str, Any] | None = None
    position: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class BoardResponse(BaseModel):
    """Response DTO for board (without lists)."""

    id: UUID
    project_id: UUID
    name: str
    description: str | None = None
    scope_config: dict[str, Any] | None = None
    is_default: bool = False
    position: int = 0
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class BoardWithListsResponse(BaseModel):
    """Response DTO for board including its lists."""

    id: UUID
    project_id: UUID
    name: str
    description: str | None = None
    scope_config: dict[str, Any] | None = None
    is_default: bool = False
    position: int = 0
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    lists: list[BoardListColumnResponse] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        from_attributes = True


class BoardListItemResponse(BaseModel):
    """Response DTO for board in list view."""

    id: UUID
    project_id: UUID
    name: str
    description: str | None = None
    scope_config: dict[str, Any] | None = None
    is_default: bool = False
    position: int = 0
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class BoardListResponse(BaseModel):
    """Response DTO for paginated board list."""

    boards: list[BoardListItemResponse]
    total: int = Field(..., description="Total number of boards")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class CreateBoardRequest(BaseModel):
    """Request DTO for creating a board."""

    name: str = Field(..., min_length=1, max_length=255, description="Board name")
    description: str | None = Field(None, max_length=65535, description="Board description")
    scope_config: dict[str, Any] | None = Field(None, description="Scope filters (e.g. label_ids)")
    is_default: bool = False
    position: int = Field(0, ge=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and strip name."""
        v = v.strip()
        if not v:
            raise ValueError("Board name cannot be empty")
        return v


class UpdateBoardRequest(BaseModel):
    """Request DTO for updating a board."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=65535)
    scope_config: dict[str, Any] | None = None
    position: int | None = Field(None, ge=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate and strip name."""
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("Board name cannot be empty")
        return v


# --- Board List (Column) DTOs ---


class CreateBoardListRequest(BaseModel):
    """Request DTO for creating a board list (column)."""

    list_type: str = Field(..., description="One of: label, assignee, milestone")
    list_config: dict[str, Any] | None = Field(
        None, description="e.g. label_id, user_id, sprint_id"
    )

    @field_validator("list_type")
    @classmethod
    def validate_list_type(cls, v: str) -> str:
        """Validate list type."""
        allowed = ("label", "assignee", "milestone")
        if v not in allowed:
            raise ValueError(f"list_type must be one of {allowed}")
        return v


class UpdateBoardListRequest(BaseModel):
    """Request DTO for updating a board list."""

    position: int | None = Field(None, ge=0)
    list_config: dict[str, Any] | None = None


class BoardListColumnListResponse(BaseModel):
    """Response DTO for list of board lists (GET /boards/:id/lists)."""

    lists: list[BoardListColumnResponse] = Field(..., description="Lists ordered by position")
    total: int = Field(..., description="Total number of lists")


# --- Board Issues (for GET /boards/:id/issues) ---


class BoardIssueItemResponse(BaseModel):
    """Issue summary for board view."""

    id: UUID
    issue_number: int
    key: str = Field(..., description="e.g. PROJ-123")
    title: str
    type: str = "task"
    status: str = "todo"
    priority: str = "medium"
    assignee_id: UUID | None = None
    story_points: int | None = None
    label_ids: list[UUID] = Field(default_factory=list)
    comment_count: int = 0
    subtask_count: int = 0

    class Config:
        """Pydantic config."""

        from_attributes = True


class BoardListWithIssuesResponse(BaseModel):
    """Board list with its issues."""

    id: UUID
    board_id: UUID
    list_type: str
    list_config: dict[str, Any] | None = None
    position: int = 0
    issues: list[BoardIssueItemResponse] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        from_attributes = True


class BoardIssuesResponse(BaseModel):
    """Response DTO for GET /boards/:id/issues."""

    lists: list[BoardListWithIssuesResponse] = Field(
        ..., description="Lists with issues grouped by column"
    )


# --- Move issue (Drag & Drop) ---


class MoveBoardIssueRequest(BaseModel):
    """Request DTO for moving an issue between board lists (drag & drop)."""

    source_list_id: UUID = Field(..., description="ID of the list the issue is moved from")
    target_list_id: UUID = Field(..., description="ID of the list the issue is moved to")
