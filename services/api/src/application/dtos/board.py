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
    organization_id: UUID | None = Field(
        None, description="Organization owning the board (for group boards)"
    )
    board_type: str = Field("project", description="Board type: project or group")
    swimlane_type: str = Field("none", description="Swimlane grouping: none, epic, or assignee")
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
    organization_id: UUID | None = Field(
        None, description="Organization owning the board (for group boards)"
    )
    board_type: str = Field("project", description="Board type: project or group")
    swimlane_type: str = Field("none", description="Swimlane grouping: none, epic, or assignee")
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
    organization_id: UUID | None = Field(
        None, description="Organization owning the board (for group boards)"
    )
    board_type: str = Field("project", description="Board type: project or group")
    swimlane_type: str = Field("none", description="Swimlane grouping: none, epic, or assignee")
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


class CreateGroupBoardRequest(BaseModel):
    """Request DTO for creating a group board at organization level."""

    name: str = Field(..., min_length=1, max_length=255, description="Board name")
    description: str | None = Field(None, max_length=65535, description="Board description")
    scope_config: dict[str, Any] | None = Field(
        None, description="Scope filters (e.g. label_ids, assignee_id, milestone_id)"
    )
    is_default: bool = False
    position: int = Field(0, ge=0)
    project_ids: list[UUID] = Field(
        ...,
        min_length=1,
        description="Projects included in the group board (first is primary project).",
    )

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
    project_id: UUID = Field(..., description="ID of the project the issue belongs to")
    project_key: str = Field(..., description="Key of the project (e.g. PROJ)")
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


class SwimlaneAssigneeSummary(BaseModel):
    """Assignee summary for assignee-based swimlane."""

    id: UUID = Field(..., description="User ID")
    name: str = Field(..., description="Display name")
    avatar_url: str | None = Field(None, description="Avatar URL")


class BoardSwimlaneResponse(BaseModel):
    """One swimlane (epic or assignee) with its columns and issues."""

    swimlane_id: UUID | None = Field(
        None, description="Epic issue ID or assignee user ID; None for 'No epic' / 'Unassigned'"
    )
    swimlane_title: str = Field(..., description="Epic title or assignee display name")
    assignee: SwimlaneAssigneeSummary | None = Field(
        None, description="Assignee details (when swimlane_type is assignee)"
    )
    lists: list[BoardListWithIssuesResponse] = Field(
        default_factory=list,
        description="Columns with issues in this swimlane",
    )


class BoardIssuesResponse(BaseModel):
    """Response DTO for GET /boards/:id/issues."""

    lists: list[BoardListWithIssuesResponse] = Field(
        default_factory=list,
        description="Lists with issues when swimlane_type is none",
    )
    swimlane_type: str = Field(
        "none",
        description="Swimlane grouping: none, epic, or assignee",
    )
    swimlanes: list[BoardSwimlaneResponse] = Field(
        default_factory=list,
        description="Swimlanes with columns and issues when swimlane_type is epic or assignee",
    )


# --- Move issue (Drag & Drop) ---


class MoveBoardIssueRequest(BaseModel):
    """Request DTO for moving an issue between board lists (drag & drop)."""

    source_list_id: UUID = Field(..., description="ID of the list the issue is moved from")
    target_list_id: UUID = Field(..., description="ID of the list the issue is moved to")


class ReorderBoardsRequest(BaseModel):
    """Request DTO for reordering boards in a project."""

    board_ids: list[UUID] = Field(
        ...,
        min_length=1,
        description="Board IDs in desired order (index = position)",
    )


class SetGroupBoardProjectsRequest(BaseModel):
    """Request DTO for setting projects on a group board."""

    project_ids: list[UUID] = Field(
        ...,
        min_length=1,
        description="Project IDs in desired order (index = position).",
    )


class UpdateBoardScopeRequest(BaseModel):
    """Request DTO for updating board scope configuration."""

    label_ids: list[UUID] | None = Field(
        None,
        description="Labels to include in board scope (issue must have at least one of them).",
    )
    exclude_label_ids: list[UUID] | None = Field(
        None,
        description="Labels to exclude from board scope (issue must have none of them).",
    )
    assignee_id: UUID | None = Field(
        None,
        description="Filter issues by assignee (global assignee filter).",
    )
    milestone_id: UUID | None = Field(
        None,
        description="Filter issues by milestone/sprint.",
    )
    types: list[str] | None = Field(
        None,
        description="Allowed issue types in scope (task, bug, story, epic).",
    )
    priorities: list[str] | None = Field(
        None,
        description="Allowed priorities in scope (low, medium, high, critical).",
    )
    fixed_user_id: UUID | None = Field(
        None,
        description="If set, board is dedicated to this user (alias of assignee filter).",
    )
    reporter_id: UUID | None = Field(
        None,
        description="Filter issues by reporter (author).",
    )
    search_text: str | None = Field(
        None,
        description="Free text search on title and description.",
    )
    story_points_min: int | None = Field(
        None,
        ge=0,
        description="Minimum story points (inclusive).",
    )
    story_points_max: int | None = Field(
        None,
        ge=0,
        description="Maximum story points (inclusive).",
    )

    @field_validator("types")
    @classmethod
    def validate_types(cls, v: list[str] | None) -> list[str] | None:
        """Validate issue types."""
        if v is None:
            return None
        allowed = {"task", "bug", "story", "epic"}
        invalid = [t for t in v if t not in allowed]
        if invalid:
            raise ValueError(f"Issue type must be one of: {', '.join(sorted(allowed))}")
        # Normalize to unique values preserving order
        seen: set[str] = set()
        result: list[str] = []
        for t in v:
            if t not in seen:
                seen.add(t)
                result.append(t)
        return result

    @field_validator("priorities")
    @classmethod
    def validate_priorities(cls, v: list[str] | None) -> list[str] | None:
        """Validate issue priorities."""
        if v is None:
            return None
        allowed = {"low", "medium", "high", "critical"}
        invalid = [p for p in v if p not in allowed]
        if invalid:
            raise ValueError(f"Issue priority must be one of: {', '.join(sorted(allowed))}")
        seen: set[str] = set()
        result: list[str] = []
        for p in v:
            if p not in seen:
                seen.add(p)
                result.append(p)
        return result


class UpdateBoardSwimlanesRequest(BaseModel):
    """Request DTO for PUT /boards/:id/swimlanes."""

    swimlane_type: str = Field(
        ...,
        description="Swimlane grouping: none, epic, or assignee",
    )

    @field_validator("swimlane_type")
    @classmethod
    def validate_swimlane_type(cls, v: str) -> str:
        """Validate swimlane type."""
        allowed = {"none", "epic", "assignee"}
        if v not in allowed:
            raise ValueError(f"swimlane_type must be one of: {', '.join(sorted(allowed))}")
        return v
