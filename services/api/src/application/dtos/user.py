"""User DTOs.

Follows Clean Architecture and DDD principles:
- UserDTO: Minimal representation for relations and display (Value Object concept)
- UserProfileDTO: Complete user profile for authentication context (Aggregate Root)
- Separation of concerns between read models and write models
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserDTO(BaseModel):
    """Minimal user representation for display and relations.

    Used in:
    - Issue assignee/reporter
    - Comment author
    - Activity actor
    - Space owner
    - Any context where basic user info is needed

    This follows the DDD Value Object pattern - immutable, lightweight,
    and focused on a specific use case (display).
    """

    id: UUID
    name: str
    email: str | None = Field(None, description="User email (optional for backward compatibility)")
    avatar_url: str | None = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class UserProfileDTO(BaseModel):
    """Complete user profile for authenticated context.

    Used in:
    - GET /api/users/me endpoint
    - User settings pages
    - Admin user management

    This follows the DDD Aggregate Root pattern - contains complete
    user information with all necessary fields for the user context.
    """

    id: UUID
    email: str
    name: str
    avatar_url: str | None = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# Alias for backward compatibility
UserResponse = UserProfileDTO


class UserUpdateRequest(BaseModel):
    """Request DTO for updating user profile."""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="User display name",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate and strip name."""
        if v is not None:
            return v.strip()
        return v


class PasswordUpdateRequest(BaseModel):
    """Request DTO for updating password."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password",
    )


class EmailUpdateRequest(BaseModel):
    """Request DTO for updating email."""

    new_email: EmailStr = Field(..., description="New email address")
    current_password: str = Field(..., description="Current password for verification")


class UserListResponse(BaseModel):
    """Response DTO for user list."""

    users: list[UserResponse]
    total: int
    page: int
    limit: int
    pages: int
