"""Integration tests for unified endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    FolderModel,
    OrganizationMemberModel,
    OrganizationModel,
    ProjectModel,
    SpaceModel,
)


@pytest.mark.asyncio
async def test_list_items_success(client: AsyncClient, test_user, db_session):
    """Test successful unified listing."""
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

    # Create folder, project, and space
    folder = FolderModel(organization_id=org.id, name="Test Folder", position=0)
    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    space = SpaceModel(
        organization_id=org.id,
        name="Test Space",
        key="TEST",
    )
    db_session.add(folder)
    db_session.add(project)
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

    # List items
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 3
    assert data["folders_count"] == 1
    assert data["nodes_count"] == 2
    assert len(data["items"]) == 3

    # Check item types
    item_types = [item["type"] for item in data["items"]]
    assert "folder" in item_types
    assert "project" in item_types
    assert "space" in item_types


@pytest.mark.asyncio
async def test_list_items_with_folder_filter(client: AsyncClient, test_user, db_session):
    """Test unified listing with folder filter."""
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
    folder = FolderModel(organization_id=org.id, name="Test Folder", position=0)
    db_session.add(folder)
    await db_session.flush()

    # Create project in folder and space without folder
    project = ProjectModel(
        organization_id=org.id,
        name="Project in Folder",
        key="PROJ",
        folder_id=folder.id,
    )
    space = SpaceModel(
        organization_id=org.id,
        name="Space without Folder",
        key="SPACE",
        folder_id=None,
    )
    db_session.add(project)
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

    # List items with folder filter
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        params={"folder_id": str(folder.id)},
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    # Should have folder + project in folder, but not space
    assert data["total"] >= 2
    # Check that project has folder_id
    project_items = [item for item in data["items"] if item["type"] == "project"]
    assert len(project_items) > 0
    assert project_items[0]["details"]["folder_id"] == str(folder.id)


@pytest.mark.asyncio
async def test_list_items_with_parent_filter(client: AsyncClient, test_user, db_session):
    """Test unified listing with parent filter."""
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

    # Create parent and child folders
    parent_folder = FolderModel(organization_id=org.id, name="Parent Folder", position=0)
    db_session.add(parent_folder)
    await db_session.flush()

    child_folder = FolderModel(
        organization_id=org.id,
        name="Child Folder",
        parent_id=parent_folder.id,
        position=0,
    )
    db_session.add(child_folder)
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

    # List items with parent filter
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        params={"parent_id": str(parent_folder.id)},
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    # Should have child folder
    folder_items = [item for item in data["items"] if item["type"] == "folder"]
    assert len(folder_items) > 0


@pytest.mark.asyncio
async def test_list_items_exclude_empty_folders(client: AsyncClient, test_user, db_session):
    """Test excluding empty folders."""
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

    # Create empty folder and folder with project
    empty_folder = FolderModel(organization_id=org.id, name="Empty Folder", position=0)
    folder_with_project = FolderModel(
        organization_id=org.id, name="Folder with Project", position=1
    )
    db_session.add(empty_folder)
    db_session.add(folder_with_project)
    await db_session.flush()

    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
        folder_id=folder_with_project.id,
    )
    db_session.add(project)
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

    # List items excluding empty folders
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        params={"include_empty_folders": False},
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    # Should have folder with project, but not empty folder
    folder_items = [item for item in data["items"] if item["type"] == "folder"]
    assert len(folder_items) == 1
    assert folder_items[0]["details"]["name"] == "Folder with Project"


@pytest.mark.asyncio
async def test_list_items_include_empty_folders(client: AsyncClient, test_user, db_session):
    """Test including empty folders."""
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

    # Create empty folder
    empty_folder = FolderModel(organization_id=org.id, name="Empty Folder", position=0)
    db_session.add(empty_folder)
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

    # List items including empty folders
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        params={"include_empty_folders": True},
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    # Should have empty folder
    assert data["folders_count"] == 1
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_list_items_empty_organization(client: AsyncClient, test_user, db_session):
    """Test listing with empty organization."""
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

    # List items
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 0
    assert data["folders_count"] == 0
    assert data["nodes_count"] == 0
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_list_items_requires_auth(client: AsyncClient):
    """Test unified listing requires authentication."""
    response = await client.get(f"/api/v1/organizations/{uuid4()}/items")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_items_requires_org_membership(client: AsyncClient, test_user, db_session):
    """Test unified listing requires organization membership."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # User is NOT a member

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

    # Try to list items
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        headers=auth_headers,
    )

    assert list_response.status_code == 403


@pytest.mark.asyncio
async def test_list_items_pagination(client: AsyncClient, test_user, db_session):
    """Test pagination."""
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

    # Create multiple items
    for i in range(5):
        folder = FolderModel(organization_id=org.id, name=f"Folder {i}", position=i)
        db_session.add(folder)
    for i in range(3):
        project = ProjectModel(
            organization_id=org.id,
            name=f"Project {i}",
            key=f"PROJ{i}",
        )
        db_session.add(project)
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

    # List items with pagination
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        params={"skip": 2, "limit": 5},
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 8  # 5 folders + 3 projects
    assert len(data["items"]) == 5  # Paginated


@pytest.mark.asyncio
async def test_list_items_validation_errors(client: AsyncClient, test_user, db_session):
    """Test validation errors."""
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

    # Test negative skip
    response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        params={"skip": -1},
        headers=auth_headers,
    )
    assert response.status_code == 422

    # Test invalid limit
    response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        params={"limit": 0},
        headers=auth_headers,
    )
    assert response.status_code == 422

    # Test limit too high
    response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        params={"limit": 2000},
        headers=auth_headers,
    )
    assert response.status_code == 422

    # Test pagination with skip greater than total
    response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        params={"skip": 1000, "limit": 10},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0  # No items in org
    assert len(data["items"]) == 0
