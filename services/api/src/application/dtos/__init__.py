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
from src.application.dtos.invitation import (
    AcceptInvitationResponse,
    CancelInvitationResponse,
    InvitationListResponse,
    InvitationResponse,
    SendInvitationRequest,
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
from src.application.dtos.organization_settings import (
    OrganizationSettingsResponse,
    UpdateOrganizationSettingsRequest,
)
from src.application.dtos.issue import (
    CreateIssueRequest,
    IssueListItemResponse,
    IssueListResponse,
    IssueResponse,
    UpdateIssueRequest,
)
from src.application.dtos.comment import (
    CommentListResponse,
    CommentListItemResponse,
    CommentResponse,
    CreateCommentRequest,
    UpdateCommentRequest,
)
from src.application.dtos.issue_activity import (
    IssueActivityListResponse,
    IssueActivityResponse,
)
from src.application.dtos.project import (
    CreateProjectRequest,
    ProjectListItemResponse,
    ProjectListResponse,
    ProjectResponse,
    UpdateProjectRequest,
)
from src.application.dtos.project_member import (
    AddProjectMemberRequest,
    ProjectMemberListResponse,
    ProjectMemberResponse,
    UpdateProjectMemberRoleRequest,
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
    # Invitation DTOs
    "InvitationResponse",
    "InvitationListResponse",
    "AcceptInvitationResponse",
    "CancelInvitationResponse",
    "SendInvitationRequest",
    # Organization Settings DTOs
    "OrganizationSettingsResponse",
    "UpdateOrganizationSettingsRequest",
    # Project DTOs
    "ProjectResponse",
    "ProjectListItemResponse",
    "ProjectListResponse",
    "CreateProjectRequest",
    "UpdateProjectRequest",
    # Project Member DTOs
    "ProjectMemberResponse",
    "ProjectMemberListResponse",
    "AddProjectMemberRequest",
    "UpdateProjectMemberRoleRequest",
    # Issue DTOs
    "IssueResponse",
    "IssueListItemResponse",
    "IssueListResponse",
    "CreateIssueRequest",
    "UpdateIssueRequest",
    # Issue Activity DTOs
    "IssueActivityResponse",
    "IssueActivityListResponse",
    # Comment DTOs
    "CommentResponse",
    "CommentListItemResponse",
    "CommentListResponse",
    "CreateCommentRequest",
    "UpdateCommentRequest",
]
