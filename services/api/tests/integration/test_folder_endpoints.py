"""Integration tests for folder endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    FolderModel,
    OrganizationMemberModel,
    OrganizationModel,
)


@pytest.mark.asyncio
async def test_create_folder_success(client: AsyncClient, test_user, db_session):
    """Test successful folder creation."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as admin
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

    # Create folder
    create_response = await client.post(
        f"/api/v1/organizations/{org.id}/folders",
        json={
            "organization_id": str(org.id),
            "name": "My New Folder",
            "position": 0,
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "My New Folder"
    assert data["organization_id"] == str(org.id)
    assert data["parent_id"] is None
    assert data["position"] == 0
    assert "id" in data


@pytest.mark.asyncio
async def test_create_folder_with_parent(client: AsyncClient, test_user, db_session):
    """Test folder creation with parent."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as admin
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Create parent folder
    parent_folder = FolderModel(
        organization_id=org.id,
        name="Parent Folder",
        position=0,
    )
    db_session.add(parent_folder)
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

    # Create child folder
    create_response = await client.post(
        f"/api/v1/organizations/{org.id}/folders",
        json={
            "organization_id": str(org.id),
            "name": "Child Folder",
            "parent_id": str(parent_folder.id),
            "position": 0,
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "Child Folder"
    assert data["parent_id"] == str(parent_folder.id)


@pytest.mark.asyncio
async def test_create_folder_requires_auth(client: AsyncClient):
    """Test folder creation requires authentication."""
    response = await client.post(
        f"/api/v1/organizations/{uuid4()}/folders",
        json={
            "organization_id": str(uuid4()),
            "name": "Test Folder",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_folder_requires_admin(client: AsyncClient, test_user, db_session):
    """Test folder creation requires admin role."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
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
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Try to create folder
    create_response = await client.post(
        f"/api/v1/organizations/{org.id}/folders",
        json={
            "organization_id": str(org.id),
            "name": "Test Folder",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 403


@pytest.mark.asyncio
async def test_list_folders_success(client: AsyncClient, test_user, db_session):
    """Test successful folder listing."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
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

    # Create folders
    folder1 = FolderModel(
        organization_id=org.id,
        name="Folder 1",
        position=0,
    )
    folder2 = FolderModel(
        organization_id=org.id,
        name="Folder 2",
        position=1,
    )
    db_session.add(folder1)
    db_session.add(folder2)
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

    # List folders
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/folders",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 2
    assert len(data["folders"]) == 2
    folder_names = [f["name"] for f in data["folders"]]
    assert "Folder 1" in folder_names
    assert "Folder 2" in folder_names


@pytest.mark.asyncio
async def test_get_folder_success(client: AsyncClient, test_user, db_session):
    """Test successful folder retrieval."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
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

    # Create folder
    folder = FolderModel(
        organization_id=org.id,
        name="Test Folder",
        position=0,
    )
    db_session.add(folder)
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

    # Get folder
    get_response = await client.get(
        f"/api/v1/organizations/{org.id}/folders/{folder.id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(folder.id)
    assert data["name"] == "Test Folder"


@pytest.mark.asyncio
async def test_update_folder_success(client: AsyncClient, test_user, db_session):
    """Test successful folder update."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as admin
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Create folder
    folder = FolderModel(
        organization_id=org.id,
        name="Original Name",
        position=0,
    )
    db_session.add(folder)
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

    # Update folder
    update_response = await client.put(
        f"/api/v1/organizations/{org.id}/folders/{folder.id}",
        json={
            "name": "Updated Name",
            "position": 1,
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Name"
    assert data["position"] == 1


@pytest.mark.asyncio
async def test_delete_folder_success(client: AsyncClient, test_user, db_session):
    """Test successful folder deletion."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as admin
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Create folder
    folder = FolderModel(
        organization_id=org.id,
        name="Folder to Delete",
        position=0,
    )
    db_session.add(folder)
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

    # Delete folder
    delete_response = await client.delete(
        f"/api/v1/organizations/{org.id}/folders/{folder.id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    # Verify folder is soft-deleted
    await db_session.refresh(folder)
    assert folder.deleted_at is not None


@pytest.mark.asyncio
async def test_get_folder_not_found(client: AsyncClient, test_user, db_session):
    """Test folder retrieval with non-existent ID."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
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
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Try to get non-existent folder
    get_response = await client.get(
        f"/api/v1/organizations/{org.id}/folders/{uuid4()}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404
