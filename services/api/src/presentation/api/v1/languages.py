"""Language management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.language import (
    SupportedLanguagesResponse,
    UpdateUserLanguageResponse,
    UserLanguagePreference,
    UserLanguageResponse,
)
from src.application.use_cases.language import (
    GetUserLanguageUseCase,
    ListSupportedLanguagesUseCase,
    UpdateUserLanguageUseCase,
)
from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.services import get_user_repository

router = APIRouter(tags=["Languages"])


# Dependency injection for use cases
def get_list_supported_languages_use_case() -> ListSupportedLanguagesUseCase:
    """Get list supported languages use case with dependencies."""
    return ListSupportedLanguagesUseCase()


def get_get_user_language_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> GetUserLanguageUseCase:
    """Get user language use case with dependencies."""
    return GetUserLanguageUseCase(user_repository)


def get_update_user_language_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UpdateUserLanguageUseCase:
    """Get update user language use case with dependencies."""
    return UpdateUserLanguageUseCase(user_repository)


@router.get(
    "/languages",
    response_model=SupportedLanguagesResponse,
    status_code=status.HTTP_200_OK,
    summary="List supported languages",
    description="Get list of all supported languages with their codes and names",
)
async def list_supported_languages(
    use_case: Annotated[
        ListSupportedLanguagesUseCase, Depends(get_list_supported_languages_use_case)
    ],
) -> SupportedLanguagesResponse:
    """List all supported languages.

    Returns a list of supported languages with their ISO 639-1 codes and names.
    No authentication required.
    """
    return await use_case.execute()


@router.get(
    "/users/me/language",
    response_model=UserLanguageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user language preference",
    description="Get the current user's language preference",
)
async def get_user_language(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetUserLanguageUseCase, Depends(get_get_user_language_use_case)],
) -> UserLanguageResponse:
    """Get current user's language preference.

    Returns the user's stored language preference.
    Requires authentication.
    """
    return await use_case.execute(current_user.id)


@router.put(
    "/users/me/language",
    response_model=UpdateUserLanguageResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user language preference",
    description="Update the current user's language preference",
)
async def update_user_language(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[UpdateUserLanguageUseCase, Depends(get_update_user_language_use_case)],
    request: UserLanguagePreference,
) -> UpdateUserLanguageResponse:
    """Update current user's language preference.

    Updates the user's language preference to one of the supported languages.
    The language code must be a valid ISO 639-1 code (e.g., 'en', 'fr', 'es', 'de').
    Requires authentication.
    """
    try:
        return await use_case.execute(current_user.id, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
