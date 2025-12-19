"""Integration tests for page and space permission endpoints."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    PageModel,
    PagePermissionModel,
    SpaceModel,
    SpacePermissionModel,
    UserModel,
)


@pytest.mark.asyncio
async def test_get_page_permissions_success(client: AsyncClient, test_user, db_session):
    """Test successful page permissions retrieval."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Create space
    space = SpaceModel(organization_id=org.id, name="Test Space", key="TEST")
    db_session.add(space)
    await db_session.flush()

    # Create page
    page = PageModel(
        space_id=space.id,
        title="Test Page",
        slug="test-page",
        created_by=test_user.id,
    )
    db_session.add(page)
    await db_session.flush()

    # Create another user
    other_user = UserModel(
        email="other@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em",
        name="Other User",
        is_active=True,
    )
    db_session.add(other_user)
    await db_session.flush()

    # Create page permission
    permission = PagePermissionModel(
        page_id=page.id,
        user_id=other_user.id,
        role="read",
        inherited_from_space=False,
    )
    db_session.add(permission)
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
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Get page permissions
    get_response = await client.get(f"/api/v1/pages/{page.id}/permissions", headers=auth_headers)

    assert get_response.status_code == 200
    data = get_response.json()
    assert len(data["permissions"]) == 1
    assert data["permissions"][0]["user_id"] == str(other_user.id)
    assert data["permissions"][0]["role"] == "read"


@pytest.mark.asyncio
async def test_update_page_permissions_success(client: AsyncClient, test_user, db_session):
    """Test successful page permissions update."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Create space
    space = SpaceModel(organization_id=org.id, name="Test Space", key="TEST")
    db_session.add(space)
    await db_session.flush()

    # Create page
    page = PageModel(
        space_id=space.id,
        title="Test Page",
        slug="test-page",
        created_by=test_user.id,
    )
    db_session.add(page)
    await db_session.flush()

    # Create another user
    other_user = UserModel(
        email="other@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em",
        name="Other User",
        is_active=True,
    )
    db_session.add(other_user)
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
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Update page permissions
    update_response = await client.put(
        f"/api/v1/pages/{page.id}/permissions",
        json={
            "permissions": [
                {
                    "user_id": str(other_user.id),
                    "role": "edit",
                }
            ]
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert len(data["permissions"]) == 1
    assert data["permissions"][0]["role"] == "edit"


@pytest.mark.asyncio
async def test_get_space_permissions_success(client: AsyncClient, test_user, db_session):
    """Test successful space permissions retrieval."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Create space
    space = SpaceModel(organization_id=org.id, name="Test Space", key="TEST")
    db_session.add(space)
    await db_session.flush()

    # Create another user
    other_user = UserModel(
        email="other@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em",
        name="Other User",
        is_active=True,
    )
    db_session.add(other_user)
    await db_session.flush()

    # Create space permission
    permission = SpacePermissionModel(
        space_id=space.id,
        user_id=other_user.id,
        role="view",
    )
    db_session.add(permission)
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
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Get space permissions
    get_response = await client.get(f"/api/v1/spaces/{space.id}/permissions", headers=auth_headers)

    assert get_response.status_code == 200
    data = get_response.json()
    assert len(data["permissions"]) == 1
    assert data["permissions"][0]["user_id"] == str(other_user.id)
    assert data["permissions"][0]["role"] == "view"


@pytest.mark.asyncio
async def test_update_space_permissions_success(client: AsyncClient, test_user, db_session):
    """Test successful space permissions update."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Create space
    space = SpaceModel(organization_id=org.id, name="Test Space", key="TEST")
    db_session.add(space)
    await db_session.flush()

    # Create another user
    other_user = UserModel(
        email="other@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em",
        name="Other User",
        is_active=True,
    )
    db_session.add(other_user)
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
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Update space permissions
    update_response = await client.put(
        f"/api/v1/spaces/{space.id}/permissions",
        json={
            "permissions": [
                {
                    "user_id": str(other_user.id),
                    "role": "edit",
                }
            ]
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert len(data["permissions"]) == 1
    assert data["permissions"][0]["role"] == "edit"


@pytest.mark.asyncio
async def test_get_page_permissions_empty(client: AsyncClient, test_user, db_session):
    """Test getting page permissions for page with no specific permissions."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Create space
    space = SpaceModel(organization_id=org.id, name="Test Space", key="TEST")
    db_session.add(space)
    await db_session.flush()

    # Create page
    page = PageModel(
        space_id=space.id,
        title="Test Page",
        slug="test-page",
        created_by=test_user.id,
    )
    db_session.add(page)
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
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Get page permissions
    get_response = await client.get(f"/api/v1/pages/{page.id}/permissions", headers=auth_headers)

    assert get_response.status_code == 200
    data = get_response.json()
    assert len(data["permissions"]) == 0
