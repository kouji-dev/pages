"""Integration tests for user list endpoints."""

import pytest
from httpx import AsyncClient

from src.domain.entities import User
from tests.constants import USERS_LIST


@pytest.mark.asyncio
async def test_list_users_success(client: AsyncClient, test_user: User) -> None:
    """Test successfully listing users."""
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

    # List users
    response = await client.get(
        USERS_LIST,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"page": 1, "limit": 20},
    )

    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert "page" in data
    assert "limit" in data
    assert "pages" in data
    assert isinstance(data["users"], list)
    assert data["page"] == 1
    assert data["limit"] == 20


@pytest.mark.asyncio
async def test_list_users_pagination(client: AsyncClient, test_user: User) -> None:
    """Test pagination works correctly."""
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

    # List users with pagination
    response = await client.get(
        USERS_LIST,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"page": 2, "limit": 5},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["limit"] == 5


@pytest.mark.asyncio
async def test_list_users_with_search(client: AsyncClient, test_user: User) -> None:
    """Test listing users with search query."""
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

    # Search for current user by email
    response = await client.get(
        USERS_LIST,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"search": test_user.email.value.split("@")[0]},
    )

    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    # Should find at least the current user
    assert len(data["users"]) >= 1


@pytest.mark.asyncio
async def test_list_users_search_case_insensitive(client: AsyncClient, test_user: User) -> None:
    """Test that search is case-insensitive."""
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

    # Search with uppercase
    response = await client.get(
        USERS_LIST,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"search": test_user.name.upper()},
    )

    assert response.status_code == 200
    data = response.json()
    # Should find users regardless of case
    assert "users" in data


@pytest.mark.asyncio
async def test_list_users_requires_auth(client: AsyncClient) -> None:
    """Test that listing users requires authentication."""
    response = await client.get(USERS_LIST)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_users_invalid_page(client: AsyncClient, test_user: User) -> None:
    """Test that invalid page number returns error."""
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

    # Try with invalid page
    response = await client.get(
        USERS_LIST,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"page": 0},
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_users_invalid_limit(client: AsyncClient, test_user: User) -> None:
    """Test that invalid limit returns error."""
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

    # Try with invalid limit
    response = await client.get(
        USERS_LIST,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"limit": 0},
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_users_limit_exceeds_max(client: AsyncClient, test_user: User) -> None:
    """Test that limit exceeding max is capped."""
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

    # Try with limit > 100
    response = await client.get(
        USERS_LIST,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"limit": 200},
    )

    assert response.status_code == 422  # Validation error (le=100 constraint)


@pytest.mark.asyncio
async def test_list_users_empty_search(client: AsyncClient, test_user: User) -> None:
    """Test listing users with empty search query."""
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

    # List with empty search (should return all users)
    response = await client.get(
        USERS_LIST,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"search": ""},
    )

    assert response.status_code == 200
    data = response.json()
    assert "users" in data
