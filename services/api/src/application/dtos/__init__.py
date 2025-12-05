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
from src.application.dtos.organization import (
    CreateOrganizationRequest,
    OrganizationListItemResponse,
    OrganizationListResponse,
    OrganizationResponse,
    UpdateOrganizationRequest,
)
from src.application.dtos.organization_member import (
    AddMemberRequest,
    OrganizationMemberListResponse,
    OrganizationMemberResponse,
    UpdateMemberRoleRequest,
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
    # Organization DTOs
    "OrganizationResponse",
    "OrganizationListItemResponse",
    "OrganizationListResponse",
    "CreateOrganizationRequest",
    "UpdateOrganizationRequest",
    # Organization Member DTOs
    "OrganizationMemberResponse",
    "OrganizationMemberListResponse",
    "AddMemberRequest",
    "UpdateMemberRoleRequest",
]
