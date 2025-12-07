"""Integration tests for space endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    SpaceModel,
)


@pytest.mark.asyncio
async def test_create_space_success(client: AsyncClient, test_user, db_session):
    """Test successful space creation."""
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

    # Create space
    create_response = await client.post(
        "/api/v1/spaces/",
        json={
            "organization_id": str(org.id),
            "name": "My New Space",
            "key": "NEW",
            "description": "A test space",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "My New Space"
    assert data["key"] == "NEW"
    assert data["description"] == "A test space"
    assert data["organization_id"] == str(org.id)
    assert data["page_count"] == 0
    assert "id" in data


@pytest.mark.asyncio
async def test_create_space_auto_key(client: AsyncClient, test_user, db_session):
    """Test space creation with auto-generated key."""
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

    # Create space without key
    create_response = await client.post(
        "/api/v1/spaces/",
        json={
            "organization_id": str(org.id),
            "name": "My Awesome Space",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "My Awesome Space"
    assert data["key"] == "MYAWESOMES"  # Auto-generated from name (max 10 chars)
    assert data["organization_id"] == str(org.id)


@pytest.mark.asyncio
async def test_create_space_requires_auth(client: AsyncClient):
    """Test space creation requires authentication."""
    response = await client.post(
        "/api/v1/spaces/",
        json={
            "organization_id": str(uuid4()),
            "name": "Test Space",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_space_requires_org_membership(client: AsyncClient, test_user, db_session):
    """Test space creation requires organization membership."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Login to get token (user is NOT a member)
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

    # Try to create space
    create_response = await client.post(
        "/api/v1/spaces/",
        json={
            "organization_id": str(org.id),
            "name": "Test Space",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 403


@pytest.mark.asyncio
async def test_get_space_success(client: AsyncClient, test_user, db_session):
    """Test successful space retrieval."""
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
    space = SpaceModel(
        organization_id=org.id,
        name="Test Space",
        key="TEST",
    )
    db_session.add(space)
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

    # Get space
    get_response = await client.get(f"/api/v1/spaces/{space.id}", headers=auth_headers)

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(space.id)
    assert data["name"] == "Test Space"
    assert data["key"] == "TEST"


@pytest.mark.asyncio
async def test_list_spaces_success(client: AsyncClient, test_user, db_session):
    """Test successful space listing."""
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

    # Create spaces
    space1 = SpaceModel(organization_id=org.id, name="Space 1", key="SPACE1")
    space2 = SpaceModel(organization_id=org.id, name="Space 2", key="SPACE2")
    db_session.add(space1)
    db_session.add(space2)
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

    # List spaces
    list_response = await client.get(
        f"/api/v1/spaces/?organization_id={org.id}", headers=auth_headers
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["spaces"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_update_space_success(client: AsyncClient, test_user, db_session):
    """Test successful space update."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as admin member
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

    # Update space
    update_response = await client.put(
        f"/api/v1/spaces/{space.id}",
        json={
            "name": "Updated Space",
            "description": "Updated description",
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Space"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_space_success(client: AsyncClient, test_user, db_session):
    """Test successful space deletion."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as admin member
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

    # Delete space
    delete_response = await client.delete(f"/api/v1/spaces/{space.id}", headers=auth_headers)

    assert delete_response.status_code == 204

    # Verify space is soft-deleted (should not appear in list)
    list_response = await client.get(
        f"/api/v1/spaces/?organization_id={org.id}", headers=auth_headers
    )
    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 0
