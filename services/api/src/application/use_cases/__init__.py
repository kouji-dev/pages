"""Application use cases."""

from src.application.use_cases.auth import (
    LoginUserUseCase,
    RefreshTokenUseCase,
    RegisterUserUseCase,
    RequestPasswordResetUseCase,
    ResetPasswordUseCase,
)
from src.application.use_cases.organization import (
    AcceptInvitationUseCase,
    AddOrganizationMemberUseCase,
    CancelInvitationUseCase,
    CreateOrganizationUseCase,
    DeleteOrganizationUseCase,
    GetOrganizationSettingsUseCase,
    GetOrganizationUseCase,
    ListInvitationsUseCase,
    ListOrganizationMembersUseCase,
    ListOrganizationsUseCase,
    RemoveOrganizationMemberUseCase,
    SendInvitationUseCase,
    UpdateOrganizationMemberRoleUseCase,
    UpdateOrganizationSettingsUseCase,
    UpdateOrganizationUseCase,
)
from src.application.use_cases.page import (
    CreatePageUseCase,
    DeletePageUseCase,
    GetPageTreeUseCase,
    GetPageUseCase,
    ListPagesUseCase,
    UpdatePageUseCase,
)
from src.application.use_cases.space import (
    CreateSpaceUseCase,
    DeleteSpaceUseCase,
    GetSpaceUseCase,
    ListSpacesUseCase,
    UpdateSpaceUseCase,
)
from src.application.use_cases.template import (
    CreateTemplateUseCase,
    DeleteTemplateUseCase,
    GetTemplateUseCase,
    ListTemplatesUseCase,
    UpdateTemplateUseCase,
)
from src.application.use_cases.user import (
    DeactivateUserUseCase,
    DeleteAvatarUseCase,
    GetUserPreferencesUseCase,
    GetUserProfileUseCase,
    ListUsersUseCase,
    ReactivateUserUseCase,
    UpdateUserEmailUseCase,
    UpdateUserPasswordUseCase,
    UpdateUserPreferencesUseCase,
    UpdateUserProfileUseCase,
    UploadAvatarUseCase,
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
    # Space use cases
    "CreateSpaceUseCase",
    "GetSpaceUseCase",
    "ListSpacesUseCase",
    "UpdateSpaceUseCase",
    "DeleteSpaceUseCase",
    # Page use cases
    "CreatePageUseCase",
    "GetPageUseCase",
    "ListPagesUseCase",
    "UpdatePageUseCase",
    "DeletePageUseCase",
    "GetPageTreeUseCase",
    # Template use cases
    "CreateTemplateUseCase",
    "GetTemplateUseCase",
    "ListTemplatesUseCase",
    "UpdateTemplateUseCase",
    "DeleteTemplateUseCase",
]
