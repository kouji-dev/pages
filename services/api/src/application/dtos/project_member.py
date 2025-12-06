"""Project member DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectMemberResponse(BaseModel):
    """Response DTO for project member data."""

    user_id: UUID
    project_id: UUID
    role: str = Field(..., description="Member role: admin, member, or viewer")
    user_name: str = Field(..., description="User display name")
    user_email: str = Field(..., description="User email address")
    avatar_url: str | None = Field(None, description="User avatar URL")
    joined_at: datetime = Field(..., description="When user joined the project")

    class Config:
        """Pydantic config."""

        from_attributes = True


class ProjectMemberListResponse(BaseModel):
    """Response DTO for paginated project member list."""

    members: list[ProjectMemberResponse]
    total: int = Field(..., description="Total number of members")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class AddProjectMemberRequest(BaseModel):
    """Request DTO for adding a member to a project."""

    user_id: UUID = Field(..., description="ID of the user to add as member")
    role: str = Field(
        default="member",
        description="Member role: admin, member, or viewer (default: member)",
    )


class UpdateProjectMemberRoleRequest(BaseModel):
    """Request DTO for updating a project member's role."""

    role: str = Field(..., description="New member role: admin, member, or viewer")
