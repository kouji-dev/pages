"""Unit tests for deactivate user use case."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.use_cases.deactivate_user import DeactivateUserUseCase
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects import Email


class TestDeactivateUserUseCase:
    """Tests for DeactivateUserUseCase."""

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
    async def test_deactivate_user_success(self, test_user) -> None:
        """Test successfully deactivating a user."""
        # Setup
        user_repository = AsyncMock()
        user_repository.get_by_id.return_value = test_user
        user_repository.update.return_value = test_user

        use_case = DeactivateUserUseCase(user_repository)

        # Execute
        await use_case.execute(str(test_user.id))

        # Assert
        assert test_user.is_deleted is True
        assert test_user.is_active is False
        assert test_user.deleted_at is not None
        user_repository.get_by_id.assert_called_once()
        user_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_user_already_deactivated(self, test_user, password_service) -> None:
        """Test deactivating an already deactivated user."""
        # Setup - user already deactivated
        test_user.deactivate()

        user_repository = AsyncMock()
        user_repository.get_by_id.return_value = test_user

        use_case = DeactivateUserUseCase(user_repository)

        # Execute
        await use_case.execute(str(test_user.id))

        # Assert - should not raise error and should not call update
        user_repository.get_by_id.assert_called_once()
        user_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_deactivate_user_not_found(self) -> None:
        """Test deactivating a non-existent user."""
        # Setup
        user_repository = AsyncMock()
        user_repository.get_by_id.return_value = None

        use_case = DeactivateUserUseCase(user_repository)

        # Execute & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))
