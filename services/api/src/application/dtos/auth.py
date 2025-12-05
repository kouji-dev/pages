"""Authentication DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Request DTO for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (min 8 chars, must include uppercase, lowercase, digit, special char)",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User display name",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and strip name."""
        return v.strip()


class RegisterResponse(BaseModel):
    """Response DTO for user registration."""

    id: UUID
    email: str
    name: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    message: str = "Registration successful"


class LoginRequest(BaseModel):
    """Request DTO for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class LoginResponse(BaseModel):
    """Response DTO for user login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token expiration in seconds")
    user: "UserBasicInfo"


class UserBasicInfo(BaseModel):
    """Basic user info included in login response."""

    id: UUID
    email: str
    name: str
    avatar_url: str | None = None
    is_verified: bool


class TokenResponse(BaseModel):
    """Response DTO for token operations."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int


class PasswordResetRequest(BaseModel):
    """Request DTO for password reset request."""

    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Request DTO for password reset confirmation."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password",
    )


class RefreshTokenRequest(BaseModel):
    """Request DTO for token refresh."""

    refresh_token: str = Field(..., description="Refresh token")


# Update forward references
LoginResponse.model_rebuild()
