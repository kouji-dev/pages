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
]
