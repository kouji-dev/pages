"""Unit tests for user profile use cases."""

import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from src.application.dtos.user import (
    EmailUpdateRequest,
    PasswordUpdateRequest,
    UserUpdateRequest,
)
from src.application.use_cases.user import (
    GetUserProfileUseCase,
    UpdateUserEmailUseCase,
    UpdateUserPasswordUseCase,
    UpdateUserProfileUseCase,
)
from src.domain.entities import User
from src.domain.exceptions import (
    AuthenticationException,
    ConflictException,
    EntityNotFoundException,
    ValidationException,
)
from src.domain.value_objects import Email, HashedPassword, Password


class TestGetUserProfileUseCase:
    """Tests for GetUserProfileUseCase."""

    @pytest.mark.asyncio
    async def test_get_user_profile_success(self) -> None:
        """Test successfully getting user profile."""
        # Setup
        user_repository = AsyncMock()
        user_id = str(uuid4())
        
        valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
        test_user = User.create(
            email=Email("test@example.com"),
            password_hash=HashedPassword(valid_hash),
            name="Test User",
        )
        
        user_repository.get_by_id.return_value = test_user
        
        use_case = GetUserProfileUseCase(user_repository)
        
        # Execute
        result = await use_case.execute(user_id)
        
        # Assert
        assert result.id == test_user.id
        assert result.email == test_user.email.value
        assert result.name == test_user.name
        user_repository.get_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_profile_not_found(self) -> None:
        """Test getting profile for non-existent user."""
        # Setup
        user_repository = AsyncMock()
        user_id = str(uuid4())
        user_repository.get_by_id.return_value = None
        
        use_case = GetUserProfileUseCase(user_repository)
        
        # Execute & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(user_id)


class TestUpdateUserProfileUseCase:
    """Tests for UpdateUserProfileUseCase."""

    @pytest.mark.asyncio
    async def test_update_user_profile_success(self) -> None:
        """Test successfully updating user profile."""
        # Setup
        user_repository = AsyncMock()
        user_id = str(uuid4())
        
        valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
        test_user = User.create(
            email=Email("test@example.com"),
            password_hash=HashedPassword(valid_hash),
            name="Test User",
        )
        
        user_repository.get_by_id.return_value = test_user
        user_repository.update.return_value = test_user
        
        request = UserUpdateRequest(name="Updated Name")
        use_case = UpdateUserProfileUseCase(user_repository)
        
        # Execute
        result = await use_case.execute(user_id, request)
        
        # Assert
        assert result.name == "Updated Name"
        user_repository.get_by_id.assert_called_once()
        user_repository.update.assert_called_once()
        assert test_user.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_user_profile_empty_name(self) -> None:
        """Test updating profile with empty name fails."""
        # Setup
        user_repository = AsyncMock()
        user_id = str(uuid4())
        
        valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
        test_user = User.create(
            email=Email("test@example.com"),
            password_hash=HashedPassword(valid_hash),
            name="Test User",
        )
        
        user_repository.get_by_id.return_value = test_user
        
        request = UserUpdateRequest(name="   ")
        use_case = UpdateUserProfileUseCase(user_repository)
        
        # Execute & Assert
        with pytest.raises(ValidationException):
            await use_case.execute(user_id, request)

    @pytest.mark.asyncio
    async def test_update_user_profile_not_found(self) -> None:
        """Test updating profile for non-existent user."""
        # Setup
        user_repository = AsyncMock()
        user_id = str(uuid4())
        user_repository.get_by_id.return_value = None
        
        request = UserUpdateRequest(name="New Name")
        use_case = UpdateUserProfileUseCase(user_repository)
        
        # Execute & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(user_id, request)


class TestUpdateUserEmailUseCase:
    """Tests for UpdateUserEmailUseCase."""

    @pytest.fixture
    def password_service(self):
        """Get password service for testing."""
        from src.infrastructure.security import BcryptPasswordService
        return BcryptPasswordService()

    @pytest.mark.asyncio
    async def test_update_user_email_success(self, password_service) -> None:
        """Test successfully updating user email."""
        # Setup
        user_repository = AsyncMock()
        user_id = str(uuid4())
        
        password = Password("CurrentPassword123!")
        hashed_password = password_service.hash(password)
        test_user = User.create(
            email=Email("old@example.com"),
            password_hash=hashed_password,
            name="Test User",
        )
        
        user_repository.get_by_id.return_value = test_user
        user_repository.exists_by_email.return_value = False
        user_repository.update.return_value = test_user
        
        request = EmailUpdateRequest(
            new_email="new@example.com",
            current_password="CurrentPassword123!",
        )
        use_case = UpdateUserEmailUseCase(user_repository, password_service)
        
        # Execute
        result = await use_case.execute(user_id, request)
        
        # Assert
        assert result.email == "new@example.com"
        assert test_user.email.value == "new@example.com"
        user_repository.exists_by_email.assert_called_once()
        user_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_email_invalid_password(self, password_service) -> None:
        """Test updating email with invalid current password fails."""
        # Setup
        user_repository = AsyncMock()
        user_id = str(uuid4())
        
        password = Password("CurrentPassword123!")
        hashed_password = password_service.hash(password)
        test_user = User.create(
            email=Email("old@example.com"),
            password_hash=hashed_password,
            name="Test User",
        )
        
        user_repository.get_by_id.return_value = test_user
        
        request = EmailUpdateRequest(
            new_email="new@example.com",
            current_password="WrongPassword123!",
        )
        use_case = UpdateUserEmailUseCase(user_repository, password_service)
        
        # Execute & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            await use_case.execute(user_id, request)
        
        assert "password" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_update_user_email_already_exists(self, password_service) -> None:
        """Test updating email to existing email fails."""
        # Setup
        user_repository = AsyncMock()
        user_id = str(uuid4())
        
        password = Password("CurrentPassword123!")
        hashed_password = password_service.hash(password)
        test_user = User.create(
            email=Email("old@example.com"),
            password_hash=hashed_password,
            name="Test User",
        )
        
        user_repository.get_by_id.return_value = test_user
        user_repository.exists_by_email.return_value = True
        
        request = EmailUpdateRequest(
            new_email="existing@example.com",
            current_password="CurrentPassword123!",
        )
        use_case = UpdateUserEmailUseCase(user_repository, password_service)
        
        # Execute & Assert
        with pytest.raises(ConflictException) as exc_info:
            await use_case.execute(user_id, request)
        
        assert "email" in str(exc_info.value).lower()


class TestUpdateUserPasswordUseCase:
    """Tests for UpdateUserPasswordUseCase."""

    @pytest.fixture
    def password_service(self):
        """Get password service for testing."""
        from src.infrastructure.security import BcryptPasswordService
        return BcryptPasswordService()

    @pytest.mark.asyncio
    async def test_update_user_password_success(self, password_service) -> None:
        """Test successfully updating user password."""
        # Setup
        user_repository = AsyncMock()
        user_id = str(uuid4())
        
        old_password = Password("OldPassword123!")
        old_hashed_password = password_service.hash(old_password)
        test_user = User.create(
            email=Email("test@example.com"),
            password_hash=old_hashed_password,
            name="Test User",
        )
        
        user_repository.get_by_id.return_value = test_user
        user_repository.update.return_value = test_user
        
        request = PasswordUpdateRequest(
            current_password="OldPassword123!",
            new_password="NewPassword123!",
        )
        use_case = UpdateUserPasswordUseCase(user_repository, password_service)
        
        # Execute
        await use_case.execute(user_id, request)
        
        # Assert
        user_repository.update.assert_called_once()
        updated_user = user_repository.update.call_args[0][0]
        
        # Verify new password works
        assert password_service.verify("NewPassword123!", updated_user.password_hash)
        
        # Verify old password doesn't work
        assert not password_service.verify("OldPassword123!", updated_user.password_hash)

    @pytest.mark.asyncio
    async def test_update_user_password_invalid_current_password(
        self, password_service
    ) -> None:
        """Test updating password with invalid current password fails."""
        # Setup
        user_repository = AsyncMock()
        user_id = str(uuid4())
        
        password = Password("CurrentPassword123!")
        hashed_password = password_service.hash(password)
        test_user = User.create(
            email=Email("test@example.com"),
            password_hash=hashed_password,
            name="Test User",
        )
        
        user_repository.get_by_id.return_value = test_user
        
        request = PasswordUpdateRequest(
            current_password="WrongPassword123!",
            new_password="NewPassword123!",
        )
        use_case = UpdateUserPasswordUseCase(user_repository, password_service)
        
        # Execute & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            await use_case.execute(user_id, request)
        
        assert "password" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_update_user_password_not_found(self, password_service) -> None:
        """Test updating password for non-existent user."""
        # Setup
        user_repository = AsyncMock()
        user_id = str(uuid4())
        user_repository.get_by_id.return_value = None
        
        request = PasswordUpdateRequest(
            current_password="OldPassword123!",
            new_password="NewPassword123!",
        )
        use_case = UpdateUserPasswordUseCase(user_repository, password_service)
        
        # Execute & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(user_id, request)

