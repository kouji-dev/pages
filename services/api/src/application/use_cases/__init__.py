"""Application use cases."""

from src.application.use_cases.auth import (
    LoginUserUseCase,
    RefreshTokenUseCase,
    RegisterUserUseCase,
    RequestPasswordResetUseCase,
    ResetPasswordUseCase,
)
from src.application.use_cases.avatar import (
    DeleteAvatarUseCase,
    UploadAvatarUseCase,
)
from src.application.use_cases.deactivate_user import DeactivateUserUseCase
from src.application.use_cases.organization import (
    CreateOrganizationUseCase,
    DeleteOrganizationUseCase,
    GetOrganizationUseCase,
    ListOrganizationsUseCase,
    UpdateOrganizationUseCase,
)
from src.application.use_cases.invitation import (
    AcceptInvitationUseCase,
    CancelInvitationUseCase,
    ListInvitationsUseCase,
    SendInvitationUseCase,
)
from src.application.use_cases.organization_member import (
    AddOrganizationMemberUseCase,
    ListOrganizationMembersUseCase,
    RemoveOrganizationMemberUseCase,
    UpdateOrganizationMemberRoleUseCase,
)
from src.application.use_cases.organization_settings import (
    GetOrganizationSettingsUseCase,
    UpdateOrganizationSettingsUseCase,
)
from src.application.use_cases.reactivate_user import ReactivateUserUseCase
from src.application.use_cases.list_users import ListUsersUseCase
from src.application.use_cases.preferences import (
    GetUserPreferencesUseCase,
    UpdateUserPreferencesUseCase,
)
from src.application.use_cases.user import (
    GetUserProfileUseCase,
    UpdateUserEmailUseCase,
    UpdateUserPasswordUseCase,
    UpdateUserProfileUseCase,
)

__all__ = [
    # Auth use cases
    "RegisterUserUseCase",
    "LoginUserUseCase",
    "RefreshTokenUseCase",
    "RequestPasswordResetUseCase",
    "ResetPasswordUseCase",
    # User use cases
    "GetUserProfileUseCase",
    "UpdateUserProfileUseCase",
    "UpdateUserEmailUseCase",
    "UpdateUserPasswordUseCase",
    # Avatar use cases
    "UploadAvatarUseCase",
    "DeleteAvatarUseCase",
    # Preferences use cases
    "GetUserPreferencesUseCase",
    "UpdateUserPreferencesUseCase",
    # List users use case
    "ListUsersUseCase",
    # Deactivate user use case
    "DeactivateUserUseCase",
    # Reactivate user use case
    "ReactivateUserUseCase",
    # Organization use cases
    "CreateOrganizationUseCase",
    "GetOrganizationUseCase",
    "ListOrganizationsUseCase",
    "UpdateOrganizationUseCase",
    "DeleteOrganizationUseCase",
    # Organization member use cases
    "AddOrganizationMemberUseCase",
    "ListOrganizationMembersUseCase",
    "UpdateOrganizationMemberRoleUseCase",
    "RemoveOrganizationMemberUseCase",
    # Invitation use cases
    "SendInvitationUseCase",
    "AcceptInvitationUseCase",
    "ListInvitationsUseCase",
    "CancelInvitationUseCase",
    # Organization settings use cases
    "GetOrganizationSettingsUseCase",
    "UpdateOrganizationSettingsUseCase",
]
