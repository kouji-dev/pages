"""Organization invitation DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SendInvitationRequest(BaseModel):
    """Request DTO for sending an invitation."""

    email: EmailStr = Field(..., description="Email address to invite")
    role: str = Field(
        default="member",
        description="Role to assign when invitation is accepted: admin, member, or viewer (default: member)",
    )


class InvitationResponse(BaseModel):
    """Response DTO for invitation data."""

    id: UUID
    organization_id: UUID
    email: str = Field(..., description="Invited email address")
    role: str = Field(..., description="Assigned role: admin, member, or viewer")
    invited_by: UUID = Field(..., description="ID of user who sent the invitation")
    expires_at: datetime = Field(..., description="Invitation expiration date")
    accepted_at: datetime | None = Field(
        None, description="When invitation was accepted (if accepted)"
    )
    created_at: datetime = Field(..., description="When invitation was created")

    class Config:
        """Pydantic config."""

        from_attributes = True


class InvitationListResponse(BaseModel):
    """Response DTO for paginated invitation list."""

    invitations: list[InvitationResponse]
    total: int = Field(..., description="Total number of invitations")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class AcceptInvitationResponse(BaseModel):
    """Response DTO for accepting an invitation."""

    organization_id: UUID = Field(..., description="Organization ID")
    organization_name: str = Field(..., description="Organization name")
    organization_slug: str = Field(..., description="Organization slug")
    role: str = Field(..., description="Assigned role")
    message: str = Field(
        default="Invitation accepted successfully",
        description="Success message",
    )


class CancelInvitationResponse(BaseModel):
    """Response DTO for canceling an invitation."""

    message: str = Field(
        default="Invitation canceled successfully",
        description="Success message",
    )
