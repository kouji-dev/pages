"""User profile management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from src.application.dtos.preferences import (
    UserPreferencesResponse,
    UserPreferencesUpdateRequest,
)
from src.application.dtos.user import (
    EmailUpdateRequest,
    PasswordUpdateRequest,
    UserResponse,
    UserUpdateRequest,
)
from src.application.use_cases.avatar import DeleteAvatarUseCase, UploadAvatarUseCase
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
from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.domain.services import PasswordService, StorageService
from src.infrastructure.config import get_settings
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.services import (
    get_password_service,
    get_storage_service,
    get_user_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_user_profile_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> GetUserProfileUseCase:
    """Get get user profile use case with dependencies."""
    return GetUserProfileUseCase(user_repository)


def get_update_user_profile_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UpdateUserProfileUseCase:
    """Get update user profile use case with dependencies."""
    return UpdateUserProfileUseCase(user_repository)


def get_update_user_email_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
) -> UpdateUserEmailUseCase:
    """Get update user email use case with dependencies."""
    return UpdateUserEmailUseCase(user_repository, password_service)


def get_update_user_password_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
) -> UpdateUserPasswordUseCase:
    """Get update user password use case with dependencies."""
    return UpdateUserPasswordUseCase(user_repository, password_service)


def get_upload_avatar_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> UploadAvatarUseCase:
    """Get upload avatar use case with dependencies."""
    return UploadAvatarUseCase(user_repository, storage_service)


def get_delete_avatar_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> DeleteAvatarUseCase:
    """Get delete avatar use case with dependencies."""
    return DeleteAvatarUseCase(user_repository, storage_service)


def get_user_preferences_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> GetUserPreferencesUseCase:
    """Get user preferences use case with dependencies."""
    return GetUserPreferencesUseCase(user_repository)


def get_update_user_preferences_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UpdateUserPreferencesUseCase:
    """Get update user preferences use case with dependencies."""
    return UpdateUserPreferencesUseCase(user_repository)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetUserProfileUseCase, Depends(get_user_profile_use_case)],
) -> UserResponse:
    """Get current user profile.

    Args:
        current_user: Current authenticated user (from dependency)
        use_case: Get user profile use case

    Returns:
        Current user profile data

    Raises:
        HTTPException: If user not found (should not happen if authenticated)
    """
    return await use_case.execute(str(current_user.id))


@router.put("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_current_user_profile(
    request: UserUpdateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[
        UpdateUserProfileUseCase, Depends(get_update_user_profile_use_case)
    ],
) -> UserResponse:
    """Update current user profile.

    Args:
        request: Profile update request (name field)
        current_user: Current authenticated user (from dependency)
        use_case: Update user profile use case

    Returns:
        Updated user profile data

    Raises:
        HTTPException: If validation fails or user not found
    """
    return await use_case.execute(str(current_user.id), request)


@router.put(
    "/me/email",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def update_current_user_email(
    request: EmailUpdateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[
        UpdateUserEmailUseCase, Depends(get_update_user_email_use_case)
    ],
) -> UserResponse:
    """Update current user email address.

    Requires current password for security.

    Args:
        request: Email update request (new_email, current_password)
        current_user: Current authenticated user (from dependency)
        use_case: Update user email use case

    Returns:
        Updated user profile data with new email

    Raises:
        HTTPException: If current password is incorrect, email already exists, or validation fails
    """
    return await use_case.execute(str(current_user.id), request)


@router.put(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_current_user_password(
    request: PasswordUpdateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[
        UpdateUserPasswordUseCase, Depends(get_update_user_password_use_case)
    ],
) -> None:
    """Update current user password.

    Requires current password for security.

    Args:
        request: Password update request (current_password, new_password)
        current_user: Current authenticated user (from dependency)
        use_case: Update user password use case

    Returns:
        No content (204) on success

    Raises:
        HTTPException: If current password is incorrect or new password validation fails
    """
    await use_case.execute(str(current_user.id), request)


@router.post(
    "/me/avatar",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_avatar(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[UploadAvatarUseCase, Depends(get_upload_avatar_use_case)],
    file: UploadFile = File(...),
) -> UserResponse:
    """Upload user avatar image.

    Accepts image files (JPEG, PNG, WEBP) up to 5MB.
    Image is automatically resized to multiple sizes (64x64, 128x128, 256x256).

    Args:
        file: Uploaded image file
        current_user: Current authenticated user (from dependency)
        use_case: Upload avatar use case

    Returns:
        Updated user profile data with new avatar URL

    Raises:
        HTTPException: If file validation fails, user not found, or storage operation fails
    """
    settings = get_settings()
    
    # Read file content
    file_content = await file.read()
    file_name = file.filename or "avatar"
    content_type = file.content_type or "application/octet-stream"

    return await use_case.execute(
        user_id=str(current_user.id),
        file_content=file_content,
        file_name=file_name,
        content_type=content_type,
        max_size_mb=settings.max_file_size_mb,
    )


@router.delete(
    "/me/avatar",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_avatar(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[DeleteAvatarUseCase, Depends(get_delete_avatar_use_case)],
) -> UserResponse:
    """Delete user avatar.

    Removes avatar image from storage and clears avatar_url in database.

    Args:
        current_user: Current authenticated user (from dependency)
        use_case: Delete avatar use case

    Returns:
        Updated user profile data with cleared avatar URL

    Raises:
        HTTPException: If user not found or storage operation fails
    """
    return await use_case.execute(str(current_user.id))


@router.get(
    "/me/preferences",
    response_model=UserPreferencesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_current_user_preferences(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[
        GetUserPreferencesUseCase, Depends(get_user_preferences_use_case)
    ],
) -> UserPreferencesResponse:
    """Get current user preferences.

    Returns default preferences if user has none set.

    Args:
        current_user: Current authenticated user (from dependency)
        use_case: Get user preferences use case

    Returns:
        User preferences response data

    Raises:
        HTTPException: If user not found (should not happen if authenticated)
    """
    return await use_case.execute(str(current_user.id))


@router.put(
    "/me/preferences",
    response_model=UserPreferencesResponse,
    status_code=status.HTTP_200_OK,
)
async def update_current_user_preferences(
    request: UserPreferencesUpdateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[
        UpdateUserPreferencesUseCase, Depends(get_update_user_preferences_use_case)
    ],
) -> UserPreferencesResponse:
    """Update current user preferences.

    Only provided fields will be updated. Other fields remain unchanged.

    Args:
        request: Preferences update request (partial update)
        current_user: Current authenticated user (from dependency)
        use_case: Update user preferences use case

    Returns:
        Updated user preferences response data

    Raises:
        HTTPException: If validation fails or user not found
    """
    return await use_case.execute(str(current_user.id), request)

