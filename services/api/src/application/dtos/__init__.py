"""Application DTOs (Data Transfer Objects)."""

from src.application.dtos.auth import (
    LoginRequest,
    LoginResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from src.application.dtos.user import (
    EmailUpdateRequest,
    PasswordUpdateRequest,
    UserResponse,
    UserUpdateRequest,
)

__all__ = [
    # Auth DTOs
    "RegisterRequest",
    "RegisterResponse",
    "LoginRequest",
    "LoginResponse",
    "TokenResponse",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "RefreshTokenRequest",
    # User DTOs
    "UserResponse",
    "UserUpdateRequest",
    "EmailUpdateRequest",
    "PasswordUpdateRequest",
]
