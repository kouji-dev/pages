"""Tests for authentication dependencies."""

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import AsyncMock, MagicMock

from src.domain.entities import User
from src.domain.exceptions import AuthenticationException
from src.domain.value_objects import Email, HashedPassword
from src.presentation.dependencies.auth import (
    get_current_active_user,
    get_current_user,
    get_optional_user,
)


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self) -> None:
        """Test successful user authentication."""
        # Setup
        token_service = MagicMock()
        user_repository = AsyncMock()
        
        # Use a valid bcrypt hash
        valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
        test_user = User.create(
            email=Email("test@example.com"),
            password_hash=HashedPassword(valid_hash),
            name="Test User",
        )
        
        token_service.get_user_id_from_token.return_value = test_user.id
        user_repository.get_by_id.return_value = test_user
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid_token",
        )
        
        # Execute
        result = await get_current_user(
            credentials=credentials,
            token_service=token_service,
            user_repository=user_repository,
        )
        
        # Assert
        assert result == test_user
        token_service.get_user_id_from_token.assert_called_once_with("valid_token")
        user_repository.get_by_id.assert_called_once_with(test_user.id)

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self) -> None:
        """Test authentication failure when no credentials provided."""
        token_service = MagicMock()
        user_repository = AsyncMock()
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                credentials=None,
                token_service=token_service,
                user_repository=user_repository,
            )
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in exc_info.value.detail
        assert "WWW-Authenticate" in exc_info.value.headers
        token_service.get_user_id_from_token.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self) -> None:
        """Test authentication failure with invalid token."""
        token_service = MagicMock()
        user_repository = AsyncMock()
        
        token_service.get_user_id_from_token.side_effect = AuthenticationException("Invalid token")
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid_token",
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                credentials=credentials,
                token_service=token_service,
                user_repository=user_repository,
            )
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token" in exc_info.value.detail
        assert "WWW-Authenticate" in exc_info.value.headers
        user_repository.get_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self) -> None:
        """Test authentication failure when user not found."""
        from uuid import uuid4
        
        token_service = MagicMock()
        user_repository = AsyncMock()
        
        user_id = uuid4()
        token_service.get_user_id_from_token.return_value = user_id
        user_repository.get_by_id.return_value = None
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid_token",
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                credentials=credentials,
                token_service=token_service,
                user_repository=user_repository,
            )
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "User not found" in exc_info.value.detail
        assert "WWW-Authenticate" in exc_info.value.headers


class TestGetCurrentActiveUser:
    """Tests for get_current_active_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_active_user_success(self) -> None:
        """Test successful active user retrieval."""
        valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
        user = User.create(
            email=Email("test@example.com"),
            password_hash=HashedPassword(valid_hash),
            name="Test User",
        )
        
        result = await get_current_active_user(current_user=user)
        
        assert result == user

    @pytest.mark.asyncio
    async def test_get_current_active_user_inactive(self) -> None:
        """Test failure when user is inactive."""
        valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
        user = User.create(
            email=Email("test@example.com"),
            password_hash=HashedPassword(valid_hash),
            name="Test User",
        )
        user.deactivate()
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(current_user=user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "deactivated" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_current_active_user_deleted(self) -> None:
        """Test failure when user is deleted."""
        valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
        user = User.create(
            email=Email("test@example.com"),
            password_hash=HashedPassword(valid_hash),
            name="Test User",
        )
        # Use deactivate() which sets deleted_at (soft delete)
        user.deactivate()
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(current_user=user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "deleted" in exc_info.value.detail.lower() or "deactivated" in exc_info.value.detail.lower()


class TestGetOptionalUser:
    """Tests for get_optional_user dependency."""

    @pytest.mark.asyncio
    async def test_get_optional_user_with_valid_credentials(self) -> None:
        """Test optional user retrieval with valid credentials."""
        token_service = MagicMock()
        user_repository = AsyncMock()
        
        valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
        test_user = User.create(
            email=Email("test@example.com"),
            password_hash=HashedPassword(valid_hash),
            name="Test User",
        )
        
        token_service.get_user_id_from_token.return_value = test_user.id
        user_repository.get_by_id.return_value = test_user
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid_token",
        )
        
        result = await get_optional_user(
            credentials=credentials,
            token_service=token_service,
            user_repository=user_repository,
        )
        
        assert result == test_user

    @pytest.mark.asyncio
    async def test_get_optional_user_no_credentials(self) -> None:
        """Test optional user returns None when no credentials."""
        token_service = MagicMock()
        user_repository = AsyncMock()
        
        result = await get_optional_user(
            credentials=None,
            token_service=token_service,
            user_repository=user_repository,
        )
        
        assert result is None
        token_service.get_user_id_from_token.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_optional_user_invalid_token(self) -> None:
        """Test optional user returns None with invalid token."""
        token_service = MagicMock()
        user_repository = AsyncMock()
        
        token_service.get_user_id_from_token.side_effect = AuthenticationException("Invalid token")
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid_token",
        )
        
        result = await get_optional_user(
            credentials=credentials,
            token_service=token_service,
            user_repository=user_repository,
        )
        
        assert result is None
        user_repository.get_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_optional_user_not_found(self) -> None:
        """Test optional user returns None when user not found."""
        from uuid import uuid4
        
        token_service = MagicMock()
        user_repository = AsyncMock()
        
        user_id = uuid4()
        token_service.get_user_id_from_token.return_value = user_id
        user_repository.get_by_id.return_value = None
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid_token",
        )
        
        result = await get_optional_user(
            credentials=credentials,
            token_service=token_service,
            user_repository=user_repository,
        )
        
        assert result is None

