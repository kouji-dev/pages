"""User management use cases."""

from src.application.use_cases.user.avatar import DeleteAvatarUseCase, UploadAvatarUseCase
from src.application.use_cases.user.deactivate import DeactivateUserUseCase
from src.application.use_cases.user.list import ListUsersUseCase
from src.application.use_cases.user.preferences import (
    GetUserPreferencesUseCase,
    UpdateUserPreferencesUseCase,
)
from src.application.use_cases.user.profile import (
    GetUserProfileUseCase,
    UpdateUserEmailUseCase,
    UpdateUserPasswordUseCase,
    UpdateUserProfileUseCase,
)
from src.application.use_cases.user.reactivate import ReactivateUserUseCase

__all__ = [
    "GetUserProfileUseCase",
    "UpdateUserProfileUseCase",
    "UpdateUserEmailUseCase",
    "UpdateUserPasswordUseCase",
    "UploadAvatarUseCase",
    "DeleteAvatarUseCase",
    "GetUserPreferencesUseCase",
    "UpdateUserPreferencesUseCase",
    "ListUsersUseCase",
    "DeactivateUserUseCase",
    "ReactivateUserUseCase",
]

