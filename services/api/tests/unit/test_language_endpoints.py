"""Unit tests for language API endpoints."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, status

from src.application.dtos.language import UserLanguagePreference
from src.application.use_cases.language import (
    GetUserLanguageUseCase,
    ListSupportedLanguagesUseCase,
    UpdateUserLanguageUseCase,
)
from src.domain.entities import User
from src.domain.value_objects import Email, HashedPassword
from src.domain.value_objects.language import Language
from src.presentation.api.v1.languages import (
    get_get_user_language_use_case,
    get_list_supported_languages_use_case,
    get_update_user_language_use_case,
    get_user_language,
    list_supported_languages,
    update_user_language,
)


@pytest.fixture
def mock_user_repository():
    """Create mock user repository."""
    return MagicMock()


@pytest.fixture
def test_user():
    """Create test user."""
    # Valid bcrypt hash for "password123"
    valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIpAZ0leVm"
    return User(
        id=MagicMock(),
        email=Email("test@example.com"),
        password_hash=HashedPassword(valid_hash),
        name="Test User",
        language=Language("en"),
    )


@pytest.fixture
def mock_update_use_case(mock_user_repository):
    """Create mock update use case."""
    use_case = UpdateUserLanguageUseCase(mock_user_repository)
    return use_case


class TestUpdateUserLanguageEndpoint:
    """Tests for update_user_language endpoint."""

    @pytest.mark.asyncio
    async def test_update_user_language_valueerror_raises_http_exception(
        self, test_user, mock_update_use_case
    ) -> None:
        """Test that ValueError from use case raises HTTPException 400."""
        # Mock use case to raise ValueError
        mock_update_use_case.execute = AsyncMock(
            side_effect=ValueError("Unsupported language: zh. Supported languages: en, fr, es, de")
        )

        request = UserLanguagePreference(language="zh")

        # Call endpoint function directly
        with pytest.raises(HTTPException) as exc_info:
            await update_user_language(
                current_user=test_user,
                use_case=mock_update_use_case,
                request=request,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Unsupported language" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_user_language_success_returns_response(
        self, test_user, mock_update_use_case
    ) -> None:
        """Test successful language update returns UpdateUserLanguageResponse."""
        from src.application.dtos.language import UpdateUserLanguageResponse

        # Mock successful update
        mock_response = UpdateUserLanguageResponse(
            language="fr", message="Language preference updated successfully"
        )
        mock_update_use_case.execute = AsyncMock(return_value=mock_response)

        request = UserLanguagePreference(language="fr")

        result = await update_user_language(
            current_user=test_user,
            use_case=mock_update_use_case,
            request=request,
        )

        assert result.language == "fr"
        assert result.message == "Language preference updated successfully"
        mock_update_use_case.execute.assert_called_once_with(test_user.id, request)


class TestLanguageDependencyInjection:
    """Tests for dependency injection functions."""

    def test_get_list_supported_languages_use_case(self) -> None:
        """Test get_list_supported_languages_use_case dependency."""
        use_case = get_list_supported_languages_use_case()
        assert isinstance(use_case, ListSupportedLanguagesUseCase)

    def test_get_get_user_language_use_case(self, mock_user_repository) -> None:
        """Test get_get_user_language_use_case dependency."""
        use_case = get_get_user_language_use_case(mock_user_repository)
        assert isinstance(use_case, GetUserLanguageUseCase)
        assert use_case._user_repository == mock_user_repository

    def test_get_update_user_language_use_case(self, mock_user_repository) -> None:
        """Test get_update_user_language_use_case dependency."""
        use_case = get_update_user_language_use_case(mock_user_repository)
        assert isinstance(use_case, UpdateUserLanguageUseCase)
        assert use_case._user_repository == mock_user_repository


class TestListSupportedLanguagesEndpoint:
    """Tests for list_supported_languages endpoint."""

    @pytest.mark.asyncio
    async def test_list_supported_languages_returns_response(self) -> None:
        """Test list_supported_languages returns SupportedLanguagesResponse."""
        from src.application.dtos.language import SupportedLanguagesResponse

        use_case = ListSupportedLanguagesUseCase()
        result = await list_supported_languages(use_case)

        assert isinstance(result, SupportedLanguagesResponse)
        assert len(result.languages) == 4  # en, fr, es, de
        language_codes = [lang.code for lang in result.languages]
        assert "en" in language_codes
        assert "fr" in language_codes
        assert "es" in language_codes
        assert "de" in language_codes


class TestGetUserLanguageEndpoint:
    """Tests for get_user_language endpoint."""

    @pytest.mark.asyncio
    async def test_get_user_language_returns_response(
        self, test_user, mock_user_repository
    ) -> None:
        """Test get_user_language returns UserLanguageResponse."""
        from src.application.dtos.language import UserLanguageResponse

        # Mock repository to return user
        mock_user_repository.get_by_id = AsyncMock(return_value=test_user)

        use_case = GetUserLanguageUseCase(mock_user_repository)
        result = await get_user_language(test_user, use_case)

        assert isinstance(result, UserLanguageResponse)
        assert result.language == "en"  # Default language
        assert result.message == "Language preference retrieved successfully"
        mock_user_repository.get_by_id.assert_called_once_with(test_user.id)
