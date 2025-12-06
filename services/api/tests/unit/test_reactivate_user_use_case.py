"""Unit tests for ReactivateUserUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.use_cases.user import ReactivateUserUseCase
from src.domain.entities import User
from src.domain.exceptions import AuthorizationException, EntityNotFoundException
from src.domain.value_objects import Email, HashedPassword


@pytest.fixture
def mock_user_repository():
    """Mock user repository."""
    return AsyncMock()


@pytest.fixture
def mock_permission_service():
    """Mock permission service."""
    return AsyncMock()


@pytest.fixture
def use_case(mock_user_repository, mock_permission_service):
    """Create ReactivateUserUseCase instance."""
    return ReactivateUserUseCase(mock_user_repository, mock_permission_service)


@pytest.fixture
def admin_user():
    """Create an admin user entity."""
    # Use a valid bcrypt hash
    valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
    return User(
        id=uuid4(),
        email=Email("admin@example.com"),
        password_hash=HashedPassword(valid_hash),
        name="Admin User",
    )


@pytest.fixture
def deactivated_user():
    """Create a deactivated user entity."""
    # Use a valid bcrypt hash
    valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
    user = User(
        id=uuid4(),
        email=Email("deactivated@example.com"),
        password_hash=HashedPassword(valid_hash),
        name="Deactivated User",
    )
    user.deactivate()
    return user


@pytest.mark.asyncio
async def test_reactivate_user_success(
    use_case, mock_user_repository, mock_permission_service, admin_user, deactivated_user
):
    """Test successful user reactivation."""
    # Setup mocks
    mock_user_repository.get_by_id.side_effect = [admin_user, deactivated_user]
    mock_permission_service.is_admin_of_any_organization.return_value = True
    mock_user_repository.update.return_value = deactivated_user

    # Execute
    await use_case.execute(str(deactivated_user.id), str(admin_user.id))

    # Assertions
    mock_user_repository.get_by_id.assert_any_call(admin_user.id)
    mock_user_repository.get_by_id.assert_any_call(deactivated_user.id)
    mock_permission_service.is_admin_of_any_organization.assert_called_once_with(admin_user)
    mock_user_repository.update.assert_called_once()

    # Verify user was reactivated
    updated_user = mock_user_repository.update.call_args[0][0]
    assert updated_user.is_active is True
    assert updated_user.is_deleted is False


@pytest.mark.asyncio
async def test_reactivate_user_not_admin(
    use_case, mock_user_repository, mock_permission_service, admin_user, deactivated_user
):
    """Test reactivation fails when user is not admin."""
    # Setup mocks
    mock_user_repository.get_by_id.return_value = admin_user
    mock_permission_service.is_admin_of_any_organization.return_value = False

    # Execute and assert
    with pytest.raises(AuthorizationException) as exc_info:
        await use_case.execute(str(deactivated_user.id), str(admin_user.id))

    assert "Only organization admins can reactivate users" in str(exc_info.value)
    mock_user_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_reactivate_user_admin_not_found(
    use_case, mock_user_repository, mock_permission_service, deactivated_user
):
    """Test reactivation fails when admin user not found."""
    # Setup mocks
    mock_user_repository.get_by_id.return_value = None

    # Execute and assert
    with pytest.raises(EntityNotFoundException) as exc_info:
        await use_case.execute(str(deactivated_user.id), str(uuid4()))

    assert "User" in str(exc_info.value)
    mock_permission_service.is_admin_of_any_organization.assert_not_called()
    mock_user_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_reactivate_user_target_not_found(
    use_case, mock_user_repository, mock_permission_service, admin_user
):
    """Test reactivation fails when target user not found."""
    # Setup mocks
    mock_user_repository.get_by_id.side_effect = [admin_user, None]
    mock_permission_service.is_admin_of_any_organization.return_value = True

    # Execute and assert
    target_user_id = str(uuid4())
    with pytest.raises(EntityNotFoundException) as exc_info:
        await use_case.execute(target_user_id, str(admin_user.id))

    assert "User" in str(exc_info.value)
    mock_user_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_reactivate_user_already_active(
    use_case, mock_user_repository, mock_permission_service, admin_user
):
    """Test reactivation is idempotent if user is already active."""
    # Setup mocks
    valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
    active_user = User(
        id=uuid4(),
        email=Email("active@example.com"),
        password_hash=HashedPassword(valid_hash),
        name="Active User",
    )
    mock_user_repository.get_by_id.side_effect = [admin_user, active_user]
    mock_permission_service.is_admin_of_any_organization.return_value = True

    # Execute (should not raise)
    await use_case.execute(str(active_user.id), str(admin_user.id))

    # Assertions
    mock_user_repository.get_by_id.assert_any_call(admin_user.id)
    mock_user_repository.get_by_id.assert_any_call(active_user.id)
    mock_permission_service.is_admin_of_any_organization.assert_called_once()
    # Should not update if already active
    mock_user_repository.update.assert_not_called()
