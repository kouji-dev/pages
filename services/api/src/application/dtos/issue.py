"""Issue DTOs."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class IssueResponse(BaseModel):
    """Response DTO for issue data."""

    id: UUID
    project_id: UUID
    issue_number: int
    key: str = Field(..., description="Issue key in format PROJ-123")
    title: str
    description: str | None = None
    type: str = Field(..., description="Issue type: task, bug, story, epic")
    status: str = Field(..., description="Issue status: todo, in_progress, done, cancelled")
    priority: str = Field(..., description="Issue priority: low, medium, high, critical")
    reporter_id: UUID | None = None
    assignee_id: UUID | None = None
    due_date: date | None = None
    story_points: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class IssueListItemResponse(BaseModel):
    """Response DTO for issue in list view."""

    id: UUID
    project_id: UUID
    issue_number: int
    key: str = Field(..., description="Issue key in format PROJ-123")
    title: str
    type: str
    status: str
    priority: str
    assignee_id: UUID | None = None
    reporter_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class IssueListResponse(BaseModel):
    """Response DTO for paginated issue list."""

    issues: list[IssueListItemResponse]
    total: int = Field(..., description="Total number of issues")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class CreateIssueRequest(BaseModel):
    """Request DTO for creating an issue."""

    project_id: UUID = Field(..., description="ID of the project the issue belongs to")
    title: str = Field(..., min_length=1, max_length=255, description="Issue title")
    description: str | None = Field(None, description="Issue description")
    type: str = Field(
        default="task",
        description="Issue type: task, bug, story, epic (default: task)",
    )
    status: str = Field(
        default="todo",
        description="Issue status: todo, in_progress, done, cancelled (default: todo)",
    )
    priority: str = Field(
        default="medium",
        description="Issue priority: low, medium, high, critical (default: medium)",
    )
    assignee_id: UUID | None = Field(None, description="ID of the user assigned to the issue")
    due_date: date | None = Field(None, description="Issue due date")
    story_points: int | None = Field(None, ge=0, description="Story points estimation")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and strip title."""
        return v.strip()

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate issue type."""
        valid_types = {"task", "bug", "story", "epic"}
        if v not in valid_types:
            raise ValueError(f"Type must be one of: {', '.join(valid_types)}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate issue status."""
        valid_statuses = {"todo", "in_progress", "done", "cancelled"}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate issue priority."""
        valid_priorities = {"low", "medium", "high", "critical"}
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return v


class UpdateIssueRequest(BaseModel):
    """Request DTO for updating an issue."""

    title: str | None = Field(None, min_length=1, max_length=255, description="Issue title")
    description: str | None = Field(None, description="Issue description")
    status: str | None = Field(None, description="Issue status: todo, in_progress, done, cancelled")
    priority: str | None = Field(None, description="Issue priority: low, medium, high, critical")
    assignee_id: UUID | None = Field(None, description="ID of the user assigned to the issue")
    due_date: date | None = Field(None, description="Issue due date")
    story_points: int | None = Field(None, ge=0, description="Story points estimation")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """Validate and strip title."""
        if v is None:
            return None
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """Validate issue status."""
        if v is None:
            return None
        valid_statuses = {"todo", "in_progress", "done", "cancelled"}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str | None) -> str | None:
        """Validate issue priority."""
        if v is None:
            return None
        valid_priorities = {"low", "medium", "high", "critical"}
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return v
