"""Unit tests for language use cases."""

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.language import UserLanguagePreference
from src.application.use_cases.language import (
    GetUserLanguageUseCase,
    ListSupportedLanguagesUseCase,
    UpdateUserLanguageUseCase,
)
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects import Email, HashedPassword
from src.domain.value_objects.language import Language


@pytest.fixture
def mock_user_repository():
    """Create mock user repository."""
    return AsyncMock()


@pytest.fixture
def test_user():
    """Create test user."""
    # Valid bcrypt hash for "password123"
    valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIpAZ0leVm"
    return User(
        id=uuid4(),
        email=Email("test@example.com"),
        password_hash=HashedPassword(valid_hash),
        name="Test User",
        language=Language("en"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


class TestGetUserLanguageUseCase:
    """Tests for GetUserLanguageUseCase."""

    @pytest.mark.asyncio
    async def test_get_user_language_success(self, mock_user_repository, test_user) -> None:
        """Test successfully getting user language preference."""
        mock_user_repository.get_by_id.return_value = test_user

        use_case = GetUserLanguageUseCase(mock_user_repository)
        result = await use_case.execute(test_user.id)

        assert result.language == "en"
        assert result.message == "Language preference retrieved successfully"
        mock_user_repository.get_by_id.assert_called_once_with(test_user.id)

    @pytest.mark.asyncio
    async def test_get_user_language_user_not_found(self, mock_user_repository) -> None:
        """Test getting language preference for non-existent user."""
        user_id = uuid4()
        mock_user_repository.get_by_id.return_value = None

        use_case = GetUserLanguageUseCase(mock_user_repository)

        with pytest.raises(EntityNotFoundException, match="User"):
            await use_case.execute(user_id)

        mock_user_repository.get_by_id.assert_called_once_with(user_id)


class TestUpdateUserLanguageUseCase:
    """Tests for UpdateUserLanguageUseCase."""

    @pytest.mark.asyncio
    async def test_update_user_language_success(self, mock_user_repository, test_user) -> None:
        """Test successfully updating user language preference."""
        mock_user_repository.get_by_id.return_value = test_user

        # Mock update to return user with new language
        updated_user = User(
            id=test_user.id,
            email=test_user.email,
            password_hash=test_user.password_hash,
            name=test_user.name,
            language=Language("fr"),
            created_at=test_user.created_at,
            updated_at=datetime.utcnow(),
        )
        mock_user_repository.update.return_value = updated_user

        use_case = UpdateUserLanguageUseCase(mock_user_repository)
        request = UserLanguagePreference(language="fr")
        result = await use_case.execute(test_user.id, request)

        assert result.language == "fr"
        assert result.message == "Language preference updated successfully"
        mock_user_repository.get_by_id.assert_called_once_with(test_user.id)
        mock_user_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_language_with_region_code(
        self, mock_user_repository, test_user
    ) -> None:
        """Test updating user language with region code."""
        mock_user_repository.get_by_id.return_value = test_user

        updated_user = User(
            id=test_user.id,
            email=test_user.email,
            password_hash=test_user.password_hash,
            name=test_user.name,
            language=Language("es-MX"),
            created_at=test_user.created_at,
            updated_at=datetime.utcnow(),
        )
        mock_user_repository.update.return_value = updated_user

        use_case = UpdateUserLanguageUseCase(mock_user_repository)
        request = UserLanguagePreference(language="es-MX")
        result = await use_case.execute(test_user.id, request)

        assert result.language == "es-mx"  # Normalized to lowercase
        mock_user_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_language_user_not_found(self, mock_user_repository) -> None:
        """Test updating language for non-existent user."""
        user_id = uuid4()
        mock_user_repository.get_by_id.return_value = None

        use_case = UpdateUserLanguageUseCase(mock_user_repository)
        request = UserLanguagePreference(language="fr")

        with pytest.raises(EntityNotFoundException, match="User"):
            await use_case.execute(user_id, request)

        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_language_invalid_code(self, mock_user_repository, test_user) -> None:
        """Test updating user language with invalid code."""
        mock_user_repository.get_by_id.return_value = test_user

        use_case = UpdateUserLanguageUseCase(mock_user_repository)
        # Use 'zh' (Chinese) which is valid length but not supported
        request = UserLanguagePreference(language="zh")

        with pytest.raises(ValueError, match="Unsupported language"):
            await use_case.execute(test_user.id, request)

        mock_user_repository.update.assert_not_called()


class TestListSupportedLanguagesUseCase:
    """Tests for ListSupportedLanguagesUseCase."""

    @pytest.mark.asyncio
    async def test_list_supported_languages(self) -> None:
        """Test listing supported languages."""
        use_case = ListSupportedLanguagesUseCase()
        result = await use_case.execute()

        assert len(result.languages) == 4  # en, fr, es, de
        language_codes = [lang.code for lang in result.languages]
        assert "en" in language_codes
        assert "fr" in language_codes
        assert "es" in language_codes
        assert "de" in language_codes

        # Check that each language has a name
        for lang in result.languages:
            assert lang.code
            assert lang.name
