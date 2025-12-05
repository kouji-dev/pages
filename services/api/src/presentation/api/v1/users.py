"""User management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from src.application.dtos.preferences import (
    UserPreferencesResponse,
    UserPreferencesUpdateRequest,
)
from src.application.dtos.user import (
    EmailUpdateRequest,
    PasswordUpdateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)
from src.application.use_cases.avatar import DeleteAvatarUseCase, UploadAvatarUseCase
from src.application.use_cases.deactivate_user import DeactivateUserUseCase
from src.application.use_cases.list_users import ListUsersUseCase
from src.application.use_cases.preferences import (
    GetUserPreferencesUseCase,
    UpdateUserPreferencesUseCase,
)
from src.application.use_cases.reactivate_user import ReactivateUserUseCase
from src.application.use_cases.user import (
    GetUserProfileUseCase,
    UpdateUserEmailUseCase,
    UpdateUserPasswordUseCase,
    UpdateUserProfileUseCase,
)
from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.domain.services import PasswordService, PermissionService, StorageService
from src.infrastructure.config import get_settings
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.services import (
    get_password_service,
    get_permission_service,
    get_storage_service,
    get_user_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_user_profile_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> GetUserProfileUseCase:
    """Get user profile use case with dependencies."""
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


def get_list_users_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> ListUsersUseCase:
    """Get list users use case with dependencies."""
    return ListUsersUseCase(user_repository)


def get_deactivate_user_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> DeactivateUserUseCase:
    """Get deactivate user use case with dependencies."""
    return DeactivateUserUseCase(user_repository)


def get_reactivate_user_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> ReactivateUserUseCase:
    """Get reactivate user use case with dependencies."""
    return ReactivateUserUseCase(user_repository, permission_service)


@router.get("/", response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def list_users(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListUsersUseCase, Depends(get_list_users_use_case)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of users per page")] = 20,
    search: Annotated[str | None, Query(description="Search query (name or email)")] = None,
    organization_id: Annotated[str | None, Query(description="Filter by organization ID")] = None,
) -> UserListResponse:
    """List users with optional search and filters."""
    return await use_case.execute(
        page=page,
        limit=limit,
        search=search,
        organization_id=organization_id,
    )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetUserProfileUseCase, Depends(get_user_profile_use_case)],
) -> UserResponse:
    """Get current user profile.

    Returns the profile of the authenticated user.

    Args:
        current_user: Current authenticated user (from dependency)
        use_case: Get user profile use case

    Returns:
        User profile data

    Raises:
        HTTPException: If user not found (should not happen if authenticated)
    """
    return await use_case.execute(str(current_user.id))


@router.put("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_current_user_profile(
    request: UserUpdateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[UpdateUserProfileUseCase, Depends(get_update_user_profile_use_case)],
) -> UserResponse:
    """Update current user profile.

    Allows updating the user's name. Email and password updates are handled
    by separate endpoints for security reasons.

    Args:
        request: Profile update request (name only)
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
    use_case: Annotated[UpdateUserEmailUseCase, Depends(get_update_user_email_use_case)],
) -> UserResponse:
    """Update current user email address.

    Requires the current password for security. After updating, the user will
    need to verify the new email address.

    Args:
        request: Email update request (new_email, current_password)
        current_user: Current authenticated user (from dependency)
        use_case: Update user email use case

    Returns:
        Updated user profile data with new email

    Raises:
        HTTPException: If password is incorrect, email is invalid/duplicate, or user not found
    """
    return await use_case.execute(str(current_user.id), request)


@router.put(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_current_user_password(
    request: PasswordUpdateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[UpdateUserPasswordUseCase, Depends(get_update_user_password_use_case)],
) -> None:
    """Update current user password.

    Requires the current password for security. The new password must meet
    the strength requirements (minimum 8 characters, etc.).

    Args:
        request: Password update request (current_password, new_password)
        current_user: Current authenticated user (from dependency)
        use_case: Update user password use case

    Returns:
        No content (204) on success

    Raises:
        HTTPException: If current password is incorrect, new password is weak, or user not found
    """
    await use_case.execute(str(current_user.id), request)


@router.post(
    "/me/avatar",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_avatar(
    current_user: Annotated[User, Depends(get_current_active_user)],
    file: Annotated[UploadFile, File(...)],
    use_case: Annotated[UploadAvatarUseCase, Depends(get_upload_avatar_use_case)],
) -> UserResponse:
    """Upload user avatar image.

    Accepts image files (JPEG, PNG, WEBP) up to 5MB. The image will be
    automatically resized and optimized.

    Args:
        current_user: Current authenticated user (from dependency)
        file: Image file to upload
        use_case: Upload avatar use case

    Returns:
        Updated user profile data with new avatar URL

    Raises:
        HTTPException: If file type/size is invalid, user not found, or upload fails
    """
    settings = get_settings()
    max_size_mb = settings.max_file_size_mb

    file_content = await file.read()
    return await use_case.execute(
        user_id=str(current_user.id),
        file_content=file_content,
        file_name=file.filename or "avatar",
        content_type=file.content_type or "image/jpeg",
        max_size_mb=max_size_mb,
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
    """Delete user avatar image.

    Removes the avatar image from storage and clears the avatar_url field.

    Args:
        current_user: Current authenticated user (from dependency)
        use_case: Delete avatar use case

    Returns:
        Updated user profile data with cleared avatar URL

    Raises:
        HTTPException: If user not found or deletion fails
    """
    return await use_case.execute(str(current_user.id))


@router.get(
    "/me/preferences",
    response_model=UserPreferencesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user_preferences(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetUserPreferencesUseCase, Depends(get_user_preferences_use_case)],
) -> UserPreferencesResponse:
    """Get current user preferences.

    Returns user preferences including theme, language, and notification settings.
    If no preferences are set, returns default preferences.

    Args:
        current_user: Current authenticated user (from dependency)
        use_case: Get user preferences use case

    Returns:
        User preferences response data

    Raises:
        HTTPException: If user not found
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


@router.post(
    "/me/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_current_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[DeactivateUserUseCase, Depends(get_deactivate_user_use_case)],
) -> None:
    """Deactivate current user account.

    Soft deletes the user by setting deleted_at timestamp and is_active=False.
    This will automatically invalidate all existing JWT tokens for this user
    since authentication checks verify is_active and is_deleted status.

    After deactivation, the user will not be able to:
    - Login with their credentials
    - Use any existing access or refresh tokens
    - Access any protected endpoints

    Args:
        current_user: Current authenticated user (from dependency)
        use_case: Deactivate user use case

    Returns:
        No content (204) on success

    Raises:
        HTTPException: If user not found (should not happen if authenticated)
    """
    await use_case.execute(str(current_user.id))


@router.post(
    "/{user_id}/reactivate",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def reactivate_user(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ReactivateUserUseCase, Depends(get_reactivate_user_use_case)],
) -> None:
    """Reactivate a deactivated user account (admin only).

    Only users who are admin of at least one organization can reactivate other users.
    This endpoint clears the deleted_at timestamp and sets is_active=True, allowing
    the user to login again and use the system.

    Args:
        user_id: ID of the user to reactivate
        current_user: Current authenticated user (must be admin of at least one org)
        use_case: Reactivate user use case

    Returns:
        No content (204) on success

    Raises:
        HTTPException: If user not found, not authorized (not admin), or target user is already active
    """
    await use_case.execute(user_id, str(current_user.id))
