"""Integration tests for user reactivation endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_reactivate_user_success(client: AsyncClient, admin_user):
    """Test successful user reactivation by admin."""
    # Login as admin to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]
    auth_headers_admin = {"Authorization": f"Bearer {admin_token}"}
    # First, create and deactivate a user
    # Register a new user
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "todeactivate@example.com",
            "password": "Password123!",
            "name": "To Deactivate",
        },
    )
    assert register_response.status_code == 201
    user_data = register_response.json()
    user_id = user_data["id"]

    # Login as the new user and deactivate
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "todeactivate@example.com",
            "password": "Password123!",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    deactivate_headers = {"Authorization": f"Bearer {token}"}

    # Deactivate the user
    deactivate_response = await client.post(
        "/api/v1/users/me/deactivate",
        headers=deactivate_headers,
    )
    assert deactivate_response.status_code == 204

    # Try to login with deactivated user (should fail)
    login_after_deactivate = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "todeactivate@example.com",
            "password": "Password123!",
        },
    )
    assert login_after_deactivate.status_code == 401
    assert "deactivated" in login_after_deactivate.json()["message"].lower()

    # Reactivate as admin
    reactivate_response = await client.post(
        f"/api/v1/users/{user_id}/reactivate",
        headers=auth_headers_admin,
    )
    assert reactivate_response.status_code == 204

    # Verify user can login again
    login_after_reactivate = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "todeactivate@example.com",
            "password": "Password123!",
        },
    )
    assert login_after_reactivate.status_code == 200


@pytest.mark.asyncio
async def test_reactivate_user_requires_auth(client: AsyncClient):
    """Test reactivation requires authentication."""
    user_id = str(uuid4())
    response = await client.post(f"/api/v1/users/{user_id}/reactivate")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_reactivate_user_requires_admin(client: AsyncClient, test_user):
    """Test reactivation requires admin role."""
    # Login as regular user (non-admin)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers_regular = {"Authorization": f"Bearer {token}"}

    user_id = str(uuid4())
    response = await client.post(
        f"/api/v1/users/{user_id}/reactivate",
        headers=auth_headers_regular,
    )
    assert response.status_code == 403
    assert "admin" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_reactivate_user_not_found(client: AsyncClient, admin_user):
    """Test reactivation fails when user not found."""
    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]
    auth_headers_admin = {"Authorization": f"Bearer {admin_token}"}

    fake_user_id = str(uuid4())
    response = await client.post(
        f"/api/v1/users/{fake_user_id}/reactivate",
        headers=auth_headers_admin,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_reactivate_user_already_active(client: AsyncClient, admin_user, test_user):
    """Test reactivating an already active user is idempotent."""
    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]
    auth_headers_admin = {"Authorization": f"Bearer {admin_token}"}

    user_id = str(test_user.id)

    # Reactivate an already active user (should succeed with 204)
    response = await client.post(
        f"/api/v1/users/{user_id}/reactivate",
        headers=auth_headers_admin,
    )
    assert response.status_code == 204
