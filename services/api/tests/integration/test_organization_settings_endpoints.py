"""Integration tests for organization settings endpoints."""

import pytest
from httpx import AsyncClient
from uuid import uuid4

from src.infrastructure.database.models import OrganizationMemberModel, OrganizationModel


@pytest.mark.asyncio
async def test_get_settings_success(client: AsyncClient, test_user, db_session) -> None:
    """Test successfully getting organization settings."""
    # Create organization
    org = OrganizationModel(
        name="Test Organization",
        slug=f"test-org-{uuid4().hex[:8]}",
    )
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="member",
    )
    db_session.add(org_member)
    await db_session.flush()

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

    # Get settings
    response = await client.get(
        f"/api/v1/organizations/{org.id}/settings",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "settings" in data
    assert "feature_flags" in data["settings"]
    assert "notifications" in data["settings"]
    assert "branding" in data["settings"]
    assert data["settings"]["feature_flags"]["advanced_analytics"] is False  # Default
    assert data["settings"]["notifications"]["email_digest"]["frequency"] == "daily"  # Default


@pytest.mark.asyncio
async def test_get_settings_requires_auth(client: AsyncClient, test_user, db_session) -> None:
    """Test that getting settings requires authentication."""
    # Create organization
    org = OrganizationModel(
        name="Test Organization",
        slug=f"test-org-{uuid4().hex[:8]}",
    )
    db_session.add(org)
    await db_session.flush()

    response = await client.get(f"/api/v1/organizations/{org.id}/settings")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_settings_requires_member(client: AsyncClient, test_user, db_session) -> None:
    """Test that getting settings requires organization membership."""
    # Create organization without adding user as member
    org = OrganizationModel(
        name="Test Organization",
        slug=f"test-org-{uuid4().hex[:8]}",
    )
    db_session.add(org)
    await db_session.flush()

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

    # Try to get settings
    response = await client.get(
        f"/api/v1/organizations/{org.id}/settings",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code in [403, 404]


@pytest.mark.asyncio
async def test_update_settings_success(client: AsyncClient, admin_user, db_session) -> None:
    """Test successfully updating settings."""
    # Create organization
    org = OrganizationModel(
        name="Test Organization",
        slug=f"test-org-{uuid4().hex[:8]}",
    )
    db_session.add(org)
    await db_session.flush()

    # Add admin_user as admin
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=admin_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Update settings
    update_response = await client.put(
        f"/api/v1/organizations/{org.id}/settings",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "settings": {
                "feature_flags": {
                    "advanced_analytics": True,
                },
                "notifications": {
                    "email_digest": {
                        "enabled": False,
                        "frequency": "weekly",
                    },
                },
            },
        },
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["settings"]["feature_flags"]["advanced_analytics"] is True
    assert data["settings"]["notifications"]["email_digest"]["enabled"] is False
    assert data["settings"]["notifications"]["email_digest"]["frequency"] == "weekly"

    # Verify settings were saved by getting them again
    get_response = await client.get(
        f"/api/v1/organizations/{org.id}/settings",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["settings"]["feature_flags"]["advanced_analytics"] is True
    assert get_data["settings"]["notifications"]["email_digest"]["enabled"] is False
    assert get_data["settings"]["notifications"]["email_digest"]["frequency"] == "weekly"


@pytest.mark.asyncio
async def test_update_settings_merges_with_existing(
    client: AsyncClient, admin_user, db_session
) -> None:
    """Test that settings are merged with existing settings."""
    # Create organization with existing settings
    import json

    org = OrganizationModel(
        name="Test Organization",
        slug=f"test-org-{uuid4().hex[:8]}",
        settings=json.dumps(
            {
                "feature_flags": {
                    "advanced_analytics": False,
                    "custom_workflows": True,
                },
                "notifications": {
                    "email_digest": {
                        "enabled": True,
                        "frequency": "daily",
                    },
                },
            }
        ),
    )
    db_session.add(org)
    await db_session.flush()

    # Add admin_user as admin
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=admin_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Update only advanced_analytics
    update_response = await client.put(
        f"/api/v1/organizations/{org.id}/settings",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "settings": {
                "feature_flags": {
                    "advanced_analytics": True,
                },
            },
        },
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["settings"]["feature_flags"]["advanced_analytics"] is True  # Updated
    assert data["settings"]["feature_flags"]["custom_workflows"] is True  # Kept
    assert data["settings"]["notifications"]["email_digest"]["enabled"] is True  # Kept


@pytest.mark.asyncio
async def test_update_settings_requires_admin(client: AsyncClient, test_user, db_session) -> None:
    """Test that updating settings requires admin role."""
    # Create organization
    org = OrganizationModel(
        name="Test Organization",
        slug=f"test-org-{uuid4().hex[:8]}",
    )
    db_session.add(org)
    await db_session.flush()

    # Add user as member (not admin)
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="member",
    )
    db_session.add(org_member)
    await db_session.flush()

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

    # Try to update settings
    response = await client.put(
        f"/api/v1/organizations/{org.id}/settings",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "settings": {
                "feature_flags": {
                    "advanced_analytics": True,
                },
            },
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_settings_invalid_frequency(
    client: AsyncClient, admin_user, db_session
) -> None:
    """Test that updating with invalid email digest frequency fails."""
    # Create organization
    org = OrganizationModel(
        name="Test Organization",
        slug=f"test-org-{uuid4().hex[:8]}",
    )
    db_session.add(org)
    await db_session.flush()

    # Add admin_user as admin
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=admin_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Try to update with invalid frequency
    response = await client.put(
        f"/api/v1/organizations/{org.id}/settings",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "settings": {
                "notifications": {
                    "email_digest": {
                        "frequency": "invalid",
                    },
                },
            },
        },
    )

    assert response.status_code in [400, 422]  # Validation error


@pytest.mark.asyncio
async def test_update_settings_invalid_feature_flag(
    client: AsyncClient, admin_user, db_session
) -> None:
    """Test that updating with invalid feature flag value fails."""
    # Create organization
    org = OrganizationModel(
        name="Test Organization",
        slug=f"test-org-{uuid4().hex[:8]}",
    )
    db_session.add(org)
    await db_session.flush()

    # Add admin_user as admin
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=admin_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Try to update with invalid feature flag value (should be boolean)
    response = await client.put(
        f"/api/v1/organizations/{org.id}/settings",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "settings": {
                "feature_flags": {
                    "advanced_analytics": "invalid",
                },
            },
        },
    )

    assert response.status_code in [400, 422]  # Validation error


@pytest.mark.asyncio
async def test_update_settings_branding(client: AsyncClient, admin_user, db_session) -> None:
    """Test updating branding settings."""
    # Create organization
    org = OrganizationModel(
        name="Test Organization",
        slug=f"test-org-{uuid4().hex[:8]}",
    )
    db_session.add(org)
    await db_session.flush()

    # Add admin_user as admin
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=admin_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Update branding
    response = await client.put(
        f"/api/v1/organizations/{org.id}/settings",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "settings": {
                "branding": {
                    "logo_url": "https://example.com/logo.png",
                    "primary_color": "#FF5733",
                    "secondary_color": "#33FF57",
                },
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["settings"]["branding"]["logo_url"] == "https://example.com/logo.png"
    assert data["settings"]["branding"]["primary_color"] == "#FF5733"
    assert data["settings"]["branding"]["secondary_color"] == "#33FF57"


@pytest.mark.asyncio
async def test_update_settings_requires_auth(client: AsyncClient, test_user, db_session) -> None:
    """Test that updating settings requires authentication."""
    # Create organization
    org = OrganizationModel(
        name="Test Organization",
        slug=f"test-org-{uuid4().hex[:8]}",
    )
    db_session.add(org)
    await db_session.flush()

    response = await client.put(
        f"/api/v1/organizations/{org.id}/settings",
        json={
            "settings": {
                "feature_flags": {
                    "advanced_analytics": True,
                },
            },
        },
    )

    assert response.status_code == 401

