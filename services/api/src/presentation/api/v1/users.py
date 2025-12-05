"""User profile management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.application.dtos.user import (
    EmailUpdateRequest,
    PasswordUpdateRequest,
    UserResponse,
    UserUpdateRequest,
)
from src.application.use_cases.user import (
    GetUserProfileUseCase,
    UpdateUserEmailUseCase,
    UpdateUserPasswordUseCase,
    UpdateUserProfileUseCase,
)
from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.domain.services import PasswordService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.services import (
    get_password_service,
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

