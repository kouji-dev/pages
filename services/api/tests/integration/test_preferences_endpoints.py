"""Integration tests for user preferences endpoints."""

import pytest
from httpx import AsyncClient

from src.domain.entities import User


@pytest.mark.asyncio
async def test_get_preferences_success(client: AsyncClient, test_user: User) -> None:
    """Test successfully getting user preferences."""
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

    # Get preferences
    response = await client.get(
        "/api/v1/users/me/preferences",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "theme" in data
    assert "language" in data
    assert "notifications" in data
    assert data["theme"] in ("light", "dark", "auto")
    assert data["language"] == "en"  # Default
    assert "email" in data["notifications"]
    assert "push" in data["notifications"]
    assert "in_app" in data["notifications"]


@pytest.mark.asyncio
async def test_get_preferences_requires_auth(client: AsyncClient) -> None:
    """Test that getting preferences requires authentication."""
    response = await client.get("/api/v1/users/me/preferences")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_preferences_success(client: AsyncClient, test_user: User) -> None:
    """Test successfully updating preferences."""
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

    # Update preferences
    update_response = await client.put(
        "/api/v1/users/me/preferences",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "theme": "dark",
            "language": "fr",
        },
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["theme"] == "dark"
    assert data["language"] == "fr"

    # Verify preferences were saved by getting them again
    get_response = await client.get(
        "/api/v1/users/me/preferences",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["theme"] == "dark"
    assert get_data["language"] == "fr"


@pytest.mark.asyncio
async def test_update_preferences_partial(client: AsyncClient, test_user: User) -> None:
    """Test that partial update only changes provided fields."""
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

    # First set both theme and language
    await client.put(
        "/api/v1/users/me/preferences",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "theme": "light",
            "language": "es",
        },
    )

    # Then update only theme
    update_response = await client.put(
        "/api/v1/users/me/preferences",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "theme": "dark",
        },
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["theme"] == "dark"
    assert data["language"] == "es"  # Should keep previous value


@pytest.mark.asyncio
async def test_update_preferences_invalid_theme(client: AsyncClient, test_user: User) -> None:
    """Test that updating with invalid theme fails."""
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

    # Try to update with invalid theme
    response = await client.put(
        "/api/v1/users/me/preferences",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "theme": "invalid_theme",
        },
    )

    assert response.status_code == 422 or response.status_code == 400  # Validation error


@pytest.mark.asyncio
async def test_update_preferences_invalid_language(client: AsyncClient, test_user: User) -> None:
    """Test that updating with invalid language fails."""
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

    # Try to update with invalid language (too long)
    response = await client.put(
        "/api/v1/users/me/preferences",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "language": "invalid",
        },
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_update_preferences_requires_auth(client: AsyncClient) -> None:
    """Test that updating preferences requires authentication."""
    response = await client.put(
        "/api/v1/users/me/preferences",
        json={
            "theme": "dark",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_preferences_notifications(client: AsyncClient, test_user: User) -> None:
    """Test updating notification preferences."""
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

    # Update notification preferences
    response = await client.put(
        "/api/v1/users/me/preferences",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "notifications": {
                "email": {
                    "enabled": False,
                    "on_issue_assigned": False,
                },
                "push": {
                    "enabled": True,
                    "on_comment_added": False,
                },
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["notifications"]["email"]["enabled"] is False
    assert data["notifications"]["email"]["on_issue_assigned"] is False
    assert data["notifications"]["push"]["enabled"] is True
    assert data["notifications"]["push"]["on_comment_added"] is False
