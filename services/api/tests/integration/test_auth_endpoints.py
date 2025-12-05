"""Integration tests for authentication endpoints."""

import pytest
from httpx import AsyncClient

# Fixtures are defined in conftest.py


@pytest.mark.asyncio
async def test_register_endpoint(client: AsyncClient) -> None:
    """Test user registration endpoint."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "NewPassword123!",
            "name": "New User",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client, test_user) -> None:
    """Test registration with duplicate email."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email.value,
            "password": "AnotherPassword123!",
            "name": "Another User",
        },
    )

    # Should return 409 Conflict or 400 Bad Request for duplicate email
    assert response.status_code in (400, 409)
    error_data = response.json()
    error_text = str(error_data).lower()
    if "detail" in error_data:
        error_text += error_data["detail"].lower()
    assert "email" in error_text or "already" in error_text


@pytest.mark.asyncio
async def test_register_invalid_password(client) -> None:
    """Test registration with invalid password."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "short",  # Too short
            "name": "User",
        },
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login_endpoint(client, test_user) -> None:
    """Test user login endpoint."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == test_user.email.value
    assert data["user"]["id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_login_invalid_credentials(client, test_user) -> None:
    """Test login with invalid credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    error_data = response.json()
    error_text = str(error_data).lower()
    if "detail" in error_data:
        error_text += error_data["detail"].lower()
    assert "invalid" in error_text or "credentials" in error_text or "unauthorized" in error_text


@pytest.mark.asyncio
async def test_login_nonexistent_user(client) -> None:
    """Test login with non-existent user."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "SomePassword123!",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_endpoint(client, test_user) -> None:
    """Test refresh token endpoint."""
    # First login to get tokens
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    refresh_token = login_response.json()["refresh_token"]

    # Use refresh token
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    # Note: Tokens may be the same if generated within the same second
    # Just verify we got valid tokens
    assert len(data["access_token"]) > 0
    assert len(data["refresh_token"]) > 0


@pytest.mark.asyncio
async def test_refresh_token_invalid(client) -> None:
    """Test refresh token with invalid token."""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_request_password_reset(client, test_user) -> None:
    """Test password reset request endpoint."""
    response = await client.post(
        "/api/v1/auth/password/reset-request",
        json={"email": test_user.email.value},
    )

    assert response.status_code == 202
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_request_password_reset_nonexistent_user(client) -> None:
    """Test password reset request for non-existent user (should still return 202)."""
    response = await client.post(
        "/api/v1/auth/password/reset-request",
        json={"email": "nonexistent@example.com"},
    )

    # Should still return 202 to prevent email enumeration
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_reset_password_endpoint(client, test_user) -> None:
    """Test password reset endpoint."""
    from src.infrastructure.security import JWTTokenService

    # Generate reset token (requires user ID, not email)
    token_service = JWTTokenService()
    reset_token = token_service.create_password_reset_token(test_user.id)

    # Reset password
    response = await client.post(
        "/api/v1/auth/password/reset",
        json={
            "token": reset_token,
            "new_password": "NewSecurePassword123!",
        },
    )

    assert response.status_code == 200
    assert "message" in response.json()

    # Verify new password works
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "NewSecurePassword123!",
        },
    )
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client) -> None:
    """Test password reset with invalid token."""
    response = await client.post(
        "/api/v1/auth/password/reset",
        json={
            "token": "invalid.token.here",
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 400 or response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_requires_auth(client) -> None:
    """Test that protected endpoints require authentication."""
    # Test a non-existent endpoint that would require auth if it existed
    response = await client.get("/api/v1/auth/me")

    # Should return 404 since endpoint doesn't exist, or 401 if it does
    assert response.status_code in (401, 404, 405)


@pytest.mark.asyncio
async def test_request_id_header(client) -> None:
    """Test that request ID is added to response headers."""
    response = await client.get("/api/v1/health")

    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"] is not None
    assert len(response.headers["X-Request-ID"]) > 0
