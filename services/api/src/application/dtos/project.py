"""Project DTOs."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.application.dtos.project_member import ProjectMemberResponse


class ProjectResponse(BaseModel):
    """Response DTO for project data."""

    id: UUID
    organization_id: UUID
    name: str
    key: str
    description: str | None = None
    settings: dict[str, Any] | None = None
    member_count: int = Field(0, description="Number of members in the project")
    issue_count: int = Field(0, description="Number of issues in the project")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ProjectListItemResponse(BaseModel):
    """Response DTO for project in list view."""

    id: UUID
    organization_id: UUID
    name: str
    key: str
    description: str | None = None
    deleted_at: datetime | None = Field(None, description="Deletion timestamp (null if active)")
    color: str | None = Field(None, description="Project color for icon background (hex code)")
    status: str = Field("active", description="Project status for UI: active, completed, on-hold")
    member_count: int = Field(0, description="Number of members in the project")
    issue_count: int = Field(0, description="Number of issues in the project")
    completed_issues_count: int = Field(
        0, description="Number of completed (done) issues in the project"
    )
    members: list[ProjectMemberResponse] = Field(
        default_factory=list, description="Top 5 project members"
    )
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ProjectListResponse(BaseModel):
    """Response DTO for paginated project list."""

    projects: list[ProjectListItemResponse]
    total: int = Field(..., description="Total number of projects")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class CreateProjectRequest(BaseModel):
    """Request DTO for creating a project."""

    organization_id: UUID = Field(..., description="ID of the organization")
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    key: str | None = Field(
        None,
        min_length=1,
        max_length=10,
        description="Project key (auto-generated from name if not provided)",
    )
    description: str | None = Field(None, max_length=1000, description="Project description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and strip name."""
        return v.strip()

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str | None) -> str | None:
        """Validate and normalize key."""
        if v is None:
            return None
        v = v.strip().upper()
        if not v:
            return None
        if len(v) > 10:
            raise ValueError("Project key cannot exceed 10 characters")
        return v


class UpdateProjectRequest(BaseModel):
    """Request DTO for updating a project."""

    name: str | None = Field(None, min_length=1, max_length=100, description="Project name")
    key: str | None = Field(
        None,
        min_length=1,
        max_length=10,
        description="Project key",
    )
    description: str | None = Field(None, max_length=1000, description="Project description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate and strip name."""
        if v is None:
            return None
        return v.strip()

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str | None) -> str | None:
        """Validate and normalize key."""
        if v is None:
            return None
        v = v.strip().upper()
        if not v:
            return None
        if len(v) > 10:
            raise ValueError("Project key cannot exceed 10 characters")
        return v
