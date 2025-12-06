"""Unit tests for user preferences use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.preferences import UserPreferencesUpdateRequest
from src.application.use_cases.user import (
    GetUserPreferencesUseCase,
    UpdateUserPreferencesUseCase,
)
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects import Email


class TestGetUserPreferencesUseCase:
    """Tests for GetUserPreferencesUseCase."""

    @pytest.fixture
    def password_service(self):
        """Get password service for creating test user."""
        from src.infrastructure.security import BcryptPasswordService

        return BcryptPasswordService()

    @pytest.fixture
    def test_user(self, password_service):
        """Create a test user without preferences."""
        from src.domain.value_objects import Password

        password = Password("TestPassword123!")
        hashed_password = password_service.hash(password)
        return User.create(
            email=Email("test@example.com"),
            password_hash=hashed_password,
            name="Test User",
        )

    @pytest.fixture
    def test_user_with_preferences(self, password_service):
        """Create a test user with custom preferences."""
        from src.domain.value_objects import Password

        password = Password("TestPassword123!")
        hashed_password = password_service.hash(password)
        user = User.create(
            email=Email("test@example.com"),
            password_hash=hashed_password,
            name="Test User",
        )
        user.preferences = {
            "theme": "dark",
            "language": "fr",
            "notifications": {
                "email": {"enabled": False},
            },
        }
        return user

    @pytest.mark.asyncio
    async def test_get_preferences_returns_defaults(self, test_user) -> None:
        """Test getting preferences returns defaults when user has none."""
        # Setup
        user_repository = AsyncMock()
        user_repository.get_by_id.return_value = test_user

        use_case = GetUserPreferencesUseCase(user_repository)

        # Execute
        result = await use_case.execute(str(test_user.id))

        # Assert
        assert result.theme == "auto"
        assert result.language == "en"
        assert result.notifications.email.enabled is True
        user_repository.get_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_preferences_returns_user_preferences(
        self, test_user_with_preferences
    ) -> None:
        """Test getting preferences returns user's custom preferences."""
        # Setup
        user_repository = AsyncMock()
        user_repository.get_by_id.return_value = test_user_with_preferences

        use_case = GetUserPreferencesUseCase(user_repository)

        # Execute
        result = await use_case.execute(str(test_user_with_preferences.id))

        # Assert
        assert result.theme == "dark"
        assert result.language == "fr"
        assert result.notifications.email.enabled is False
        user_repository.get_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_preferences_user_not_found(self) -> None:
        """Test getting preferences for non-existent user."""
        # Setup
        user_repository = AsyncMock()
        user_repository.get_by_id.return_value = None

        use_case = GetUserPreferencesUseCase(user_repository)

        # Execute & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestUpdateUserPreferencesUseCase:
    """Tests for UpdateUserPreferencesUseCase."""

    @pytest.fixture
    def password_service(self):
        """Get password service for creating test user."""
        from src.infrastructure.security import BcryptPasswordService

        return BcryptPasswordService()

    @pytest.fixture
    def test_user(self, password_service):
        """Create a test user."""
        from src.domain.value_objects import Password

        password = Password("TestPassword123!")
        hashed_password = password_service.hash(password)
        return User.create(
            email=Email("test@example.com"),
            password_hash=hashed_password,
            name="Test User",
        )

    @pytest.mark.asyncio
    async def test_update_preferences_success(self, test_user) -> None:
        """Test successfully updating preferences."""
        # Setup
        user_repository = AsyncMock()
        user_repository.get_by_id.return_value = test_user
        user_repository.update.return_value = test_user

        use_case = UpdateUserPreferencesUseCase(user_repository)
        request = UserPreferencesUpdateRequest(theme="dark", language="fr")

        # Execute
        result = await use_case.execute(str(test_user.id), request)

        # Assert
        assert result.theme == "dark"
        assert result.language == "fr"
        user_repository.get_by_id.assert_called_once()
        user_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_preferences_partial_update(self, test_user) -> None:
        """Test updating only theme keeps other preferences."""
        # Setup
        test_user.preferences = {
            "theme": "light",
            "language": "en",
            "notifications": {
                "email": {"enabled": True},
            },
        }

        user_repository = AsyncMock()
        user_repository.get_by_id.return_value = test_user
        user_repository.update.return_value = test_user

        use_case = UpdateUserPreferencesUseCase(user_repository)
        request = UserPreferencesUpdateRequest(theme="dark")

        # Execute
        result = await use_case.execute(str(test_user.id), request)

        # Assert - theme updated, language kept
        assert result.theme == "dark"
        assert result.language == "en"  # Should keep original

    @pytest.mark.asyncio
    async def test_update_preferences_invalid_theme(self, test_user) -> None:
        """Test updating preferences with invalid theme fails at Pydantic validation."""
        # Execute & Assert - Pydantic validates before reaching use case
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            # This should fail at Pydantic validation level
            UserPreferencesUpdateRequest(theme="invalid_theme")

    @pytest.mark.asyncio
    async def test_update_preferences_user_not_found(self) -> None:
        """Test updating preferences for non-existent user."""
        # Setup
        user_repository = AsyncMock()
        user_repository.get_by_id.return_value = None

        use_case = UpdateUserPreferencesUseCase(user_repository)
        request = UserPreferencesUpdateRequest(theme="dark")

        # Execute & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()), request)

    @pytest.mark.asyncio
    async def test_update_preferences_notifications(self, test_user) -> None:
        """Test updating notification preferences."""
        # Setup
        user_repository = AsyncMock()
        user_repository.get_by_id.return_value = test_user
        user_repository.update.return_value = test_user

        use_case = UpdateUserPreferencesUseCase(user_repository)
        request = UserPreferencesUpdateRequest(
            notifications={
                "email": {
                    "enabled": False,
                    "on_issue_assigned": False,
                }
            }
        )

        # Execute
        result = await use_case.execute(str(test_user.id), request)

        # Assert
        assert result.notifications.email.enabled is False
        assert result.notifications.email.on_issue_assigned is False
        user_repository.update.assert_called_once()
