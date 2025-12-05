"""Integration tests for user deactivation endpoint."""

import pytest
from httpx import AsyncClient

from src.domain.entities import User


@pytest.mark.asyncio
async def test_deactivate_user_success(client: AsyncClient, test_user: User) -> None:
    """Test successfully deactivating user account."""
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
    response = await client.post(
        "/api/v1/users/me/deactivate",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 204

    # Verify user cannot login anymore
    login_after_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )

    assert login_after_response.status_code == 401
    error_data = login_after_response.json()
    # Check for error message in detail or message field
    error_message = (error_data.get("detail", "") or error_data.get("message", "")).lower()
    # The error should mention deactivation - check both possible formats
    assert "deactivated" in error_message or "inactive" in error_message


@pytest.mark.asyncio
async def test_deactivate_user_invalidates_tokens(client: AsyncClient, test_user: User) -> None:
    """Test that deactivation invalidates existing tokens."""
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

    # Verify token works before deactivation
    profile_response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert profile_response.status_code == 200

    # Deactivate user
    deactivate_response = await client.post(
        "/api/v1/users/me/deactivate",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert deactivate_response.status_code == 204

    # Verify token is now invalid (user is deactivated)
    profile_after_response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert profile_after_response.status_code == 403
    error_message = profile_after_response.json().get("detail", "").lower()
    assert "deactivated" in error_message or "deleted" in error_message


@pytest.mark.asyncio
async def test_deactivate_user_requires_auth(client: AsyncClient) -> None:
    """Test that deactivating user requires authentication."""
    response = await client.post("/api/v1/users/me/deactivate")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_deactivate_user_cannot_reactivate_via_login(client: AsyncClient, test_user: User) -> None:
    """Test that deactivated user cannot login to reactivate."""
    # Login first
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Deactivate
    deactivate_response = await client.post(
        "/api/v1/users/me/deactivate",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert deactivate_response.status_code == 204

    # Try to login again (should fail)
    login_after_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )

    assert login_after_response.status_code == 401

