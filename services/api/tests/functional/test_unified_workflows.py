"""Functional tests for unified workflows."""

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
async def test_unified_list_workflow(client: AsyncClient, test_user, db_session):
    """Test complete workflow of creating and listing unified items."""
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

    # Create folder
    folder = FolderModel(organization_id=org.id, name="My Folder", position=0)
    db_session.add(folder)
    await db_session.flush()

    # Create project
    project = ProjectModel(
        organization_id=org.id,
        name="My Project",
        key="PROJ",
        description="A test project",
    )
    db_session.add(project)
    await db_session.flush()

    # Create space
    space = SpaceModel(
        organization_id=org.id,
        name="My Space",
        key="SPACE",
        description="A test space",
    )
    db_session.add(space)
    await db_session.flush()

    # List unified items
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 3
    assert data["folders_count"] == 1
    assert data["nodes_count"] == 2

    # Verify structure
    folder_item = next(item for item in data["items"] if item["type"] == "folder")
    assert folder_item["details"]["name"] == "My Folder"
    assert folder_item["position"] == 0

    project_item = next(item for item in data["items"] if item["type"] == "project")
    assert project_item["details"]["name"] == "My Project"
    assert project_item["details"]["key"] == "PROJ"
    assert project_item["details"]["description"] == "A test project"

    space_item = next(item for item in data["items"] if item["type"] == "space")
    assert space_item["details"]["name"] == "My Space"
    assert space_item["details"]["key"] == "SPACE"
    assert space_item["details"]["description"] == "A test space"


@pytest.mark.asyncio
async def test_unified_list_with_folder_assignment(client: AsyncClient, test_user, db_session):
    """Test assigning nodes to folders and listing."""
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

    # Create folder
    folder = FolderModel(organization_id=org.id, name="Development", position=0)
    db_session.add(folder)
    await db_session.flush()

    # Create projects
    project1 = ProjectModel(
        organization_id=org.id,
        name="Frontend",
        key="FE",
        folder_id=folder.id,
    )
    project2 = ProjectModel(
        organization_id=org.id,
        name="Backend",
        key="BE",
        folder_id=folder.id,
    )
    project3 = ProjectModel(
        organization_id=org.id,
        name="Standalone",
        key="SA",
        folder_id=None,
    )
    db_session.add(project1)
    db_session.add(project2)
    db_session.add(project3)
    await db_session.flush()

    # List all items
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["folders_count"] == 1
    assert data["nodes_count"] == 3

    # Filter by folder
    filtered_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        params={"folder_id": str(folder.id)},
        headers=auth_headers,
    )

    assert filtered_response.status_code == 200
    filtered_data = filtered_response.json()
    # Should have folder + 2 projects in folder
    project_items = [item for item in filtered_data["items"] if item["type"] == "project"]
    assert len(project_items) == 2
    for project_item in project_items:
        assert project_item["details"]["folder_id"] == str(folder.id)


@pytest.mark.asyncio
async def test_unified_list_organization_isolation(client: AsyncClient, test_user, db_session):
    """Test isolation between organizations."""
    # Create two organizations
    org1 = OrganizationModel(name="Org 1", slug="org-1")
    org2 = OrganizationModel(name="Org 2", slug="org-2")
    db_session.add(org1)
    db_session.add(org2)
    await db_session.flush()

    # Add user as member of org1 only
    org_member = OrganizationMemberModel(
        organization_id=org1.id,
        user_id=test_user.id,
        role="member",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Create items in both organizations
    folder1 = FolderModel(organization_id=org1.id, name="Org1 Folder", position=0)
    folder2 = FolderModel(organization_id=org2.id, name="Org2 Folder", position=0)
    project1 = ProjectModel(
        organization_id=org1.id,
        name="Org1 Project",
        key="O1P",
    )
    project2 = ProjectModel(
        organization_id=org2.id,
        name="Org2 Project",
        key="O2P",
    )
    db_session.add(folder1)
    db_session.add(folder2)
    db_session.add(project1)
    db_session.add(project2)
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

    # List items for org1
    list_response = await client.get(
        f"/api/v1/organizations/{org1.id}/items",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 2  # 1 folder + 1 project
    # Verify items belong to org1
    for item in data["items"]:
        assert item["organization_id"] == str(org1.id)

    # Try to list items for org2 (should fail - not a member)
    list_response2 = await client.get(
        f"/api/v1/organizations/{org2.id}/items",
        headers=auth_headers,
    )

    assert list_response2.status_code == 403


@pytest.mark.asyncio
async def test_unified_list_filtering_workflow(client: AsyncClient, test_user, db_session):
    """Test complex filtering workflow."""
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

    # Create hierarchical folders
    root_folder = FolderModel(organization_id=org.id, name="Root", position=0)
    db_session.add(root_folder)
    await db_session.flush()

    child_folder = FolderModel(
        organization_id=org.id,
        name="Child",
        parent_id=root_folder.id,
        position=0,
    )
    db_session.add(child_folder)
    await db_session.flush()

    # Create projects in different folders
    project1 = ProjectModel(
        organization_id=org.id,
        name="Project 1",
        key="P1",
        folder_id=root_folder.id,
    )
    project2 = ProjectModel(
        organization_id=org.id,
        name="Project 2",
        key="P2",
        folder_id=child_folder.id,
    )
    project3 = ProjectModel(
        organization_id=org.id,
        name="Project 3",
        key="P3",
        folder_id=None,
    )
    db_session.add(project1)
    db_session.add(project2)
    db_session.add(project3)
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

    # Filter by parent_id
    parent_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        params={"parent_id": str(root_folder.id)},
        headers=auth_headers,
    )

    assert parent_response.status_code == 200
    parent_data = parent_response.json()
    # Should have child folder
    folder_items = [item for item in parent_data["items"] if item["type"] == "folder"]
    assert len(folder_items) > 0

    # Filter by folder_id
    folder_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        params={"folder_id": str(root_folder.id)},
        headers=auth_headers,
    )

    assert folder_response.status_code == 200
    folder_data = folder_response.json()
    # Should have project1
    project_items = [item for item in folder_data["items"] if item["type"] == "project"]
    assert len(project_items) > 0


@pytest.mark.asyncio
async def test_unified_list_empty_folders_workflow(client: AsyncClient, test_user, db_session):
    """Test workflow with empty folders."""
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

    # Create empty folder and folder with content
    empty_folder = FolderModel(organization_id=org.id, name="Empty", position=0)
    full_folder = FolderModel(organization_id=org.id, name="Full", position=1)
    db_session.add(empty_folder)
    db_session.add(full_folder)
    await db_session.flush()

    project = ProjectModel(
        organization_id=org.id,
        name="Project",
        key="PROJ",
        folder_id=full_folder.id,
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

    # Include empty folders
    include_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        params={"include_empty_folders": True},
        headers=auth_headers,
    )

    assert include_response.status_code == 200
    include_data = include_response.json()
    assert include_data["folders_count"] == 2

    # Exclude empty folders
    exclude_response = await client.get(
        f"/api/v1/organizations/{org.id}/items",
        params={"include_empty_folders": False},
        headers=auth_headers,
    )

    assert exclude_response.status_code == 200
    exclude_data = exclude_response.json()
    # Should only have folder with project
    assert exclude_data["folders_count"] == 1
    folder_items = [item for item in exclude_data["items"] if item["type"] == "folder"]
    assert len(folder_items) == 1
    assert folder_items[0]["details"]["name"] == "Full"
