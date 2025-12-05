"""Integration tests for user profile endpoints."""

import pytest
from httpx import AsyncClient

from src.domain.entities import User
from src.domain.value_objects import Email, Password
from src.infrastructure.security import BcryptPasswordService, JWTTokenService

# Fixtures are defined in conftest.py


@pytest.mark.asyncio
async def test_get_current_user_profile(
    client: AsyncClient, test_user: User
) -> None:
    """Test getting current user profile."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Get profile
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email.value
    assert data["name"] == test_user.name
    assert data["is_active"] is True
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_current_user_profile_requires_auth(
    client: AsyncClient,
) -> None:
    """Test that getting profile requires authentication."""
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 401
    # FastAPI's HTTPBearer returns 403 with detail, or 401 with WWW-Authenticate header
    # The exact format may vary, so just check status code


@pytest.mark.asyncio
async def test_update_user_profile_name(
    client: AsyncClient, test_user: User
) -> None:
    """Test updating user profile name."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Update profile
    response = await client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "Updated Name"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email.value

    # Verify change persisted by getting profile again
    get_response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_update_user_profile_empty_name_fails(
    client: AsyncClient, test_user: User
) -> None:
    """Test that updating profile with empty name fails."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Try to update with empty name (whitespace only)
    response = await client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "   "},
    )

    assert response.status_code == 422 or response.status_code == 400
    # Should return validation error


@pytest.mark.asyncio
async def test_update_user_email_success(
    client: AsyncClient, test_user: User
) -> None:
    """Test successfully updating user email."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Update email
    new_email = "newemail@example.com"
    response = await client.put(
        "/api/v1/users/me/email",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "new_email": new_email,
            "current_password": "TestPassword123!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == new_email
    assert data["id"] == str(test_user.id)

    # Verify can login with new email
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": new_email,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_update_user_email_invalid_password(
    client: AsyncClient, test_user: User
) -> None:
    """Test that updating email with wrong password fails."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Try to update email with wrong password
    response = await client.put(
        "/api/v1/users/me/email",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "new_email": "newemail@example.com",
            "current_password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    error_data = response.json()
    error_text = error_data.get("message", "").lower()
    assert "password" in error_text or "invalid" in error_text


@pytest.mark.asyncio
async def test_update_user_email_duplicate_fails(
    client: AsyncClient, test_user: User
) -> None:
    """Test that updating email to existing email fails."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Create another user first
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "other@example.com",
            "password": "OtherPassword123!",
            "name": "Other User",
        },
    )
    assert register_response.status_code == 201

    # Try to update email to existing email
    response = await client.put(
        "/api/v1/users/me/email",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "new_email": "other@example.com",
            "current_password": "TestPassword123!",
        },
    )

    assert response.status_code == 409 or response.status_code == 400
    error_data = response.json()
    error_text = error_data.get("message", "").lower()
    assert "email" in error_text or "already" in error_text


@pytest.mark.asyncio
async def test_update_user_password_success(
    client: AsyncClient, test_user: User
) -> None:
    """Test successfully updating user password."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Update password
    new_password = "NewPassword123!"
    response = await client.put(
        "/api/v1/users/me/password",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "current_password": "TestPassword123!",
            "new_password": new_password,
        },
    )

    assert response.status_code == 204  # No content

    # Verify old password doesn't work
    old_login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert old_login_response.status_code == 401

    # Verify new password works
    new_login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": new_password,
        },
    )
    assert new_login_response.status_code == 200


@pytest.mark.asyncio
async def test_update_user_password_invalid_current_password(
    client: AsyncClient, test_user: User
) -> None:
    """Test that updating password with wrong current password fails."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Try to update password with wrong current password
    response = await client.put(
        "/api/v1/users/me/password",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 401
    error_data = response.json()
    error_text = error_data.get("message", "").lower()
    assert "password" in error_text or "invalid" in error_text


@pytest.mark.asyncio
async def test_update_user_password_weak_password_fails(
    client: AsyncClient, test_user: User
) -> None:
    """Test that updating password with weak password fails."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Try to update password with weak password
    response = await client.put(
        "/api/v1/users/me/password",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "current_password": "TestPassword123!",
            "new_password": "short",  # Too short
        },
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_update_profile_requires_active_user(
    client: AsyncClient, test_user: User, db_session
) -> None:
    """Test that deactivated user cannot update profile."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Deactivate user
    from src.infrastructure.database.repositories import SQLAlchemyUserRepository

    user_repo = SQLAlchemyUserRepository(db_session)
    test_user.deactivate()
    await user_repo.update(test_user)
    await db_session.flush()

    # Try to update profile
    response = await client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "New Name"},
    )

    # Should fail because user is deactivated
    assert response.status_code == 401 or response.status_code == 403

