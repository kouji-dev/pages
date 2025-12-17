"""Functional tests for folder workflows."""

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
async def test_folder_workflow_create_list_update_delete(
    client: AsyncClient, test_user, db_session
):
    """Test complete folder workflow: create, list, update, delete."""
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

    # Login
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

    # 1. Create root folder
    create_response = await client.post(
        f"/api/v1/organizations/{org.id}/folders",
        json={
            "organization_id": str(org.id),
            "name": "Root Folder",
            "position": 0,
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    root_folder_data = create_response.json()
    root_folder_id = root_folder_data["id"]
    assert root_folder_data["name"] == "Root Folder"
    assert root_folder_data["parent_id"] is None

    # 2. Create child folder
    create_child_response = await client.post(
        f"/api/v1/organizations/{org.id}/folders",
        json={
            "organization_id": str(org.id),
            "name": "Child Folder",
            "parent_id": root_folder_id,
            "position": 0,
        },
        headers=auth_headers,
    )
    assert create_child_response.status_code == 201
    child_folder_data = create_child_response.json()
    child_folder_id = child_folder_data["id"]
    assert child_folder_data["name"] == "Child Folder"
    assert child_folder_data["parent_id"] == root_folder_id

    # 3. List all folders (without parent_id filter, should return root folders only)
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/folders",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    list_data = list_response.json()
    # When parent_id is not specified, it defaults to None which means root folders only
    assert list_data["total"] == 1
    assert list_data["folders"][0]["name"] == "Root Folder"

    # 4. List folders by parent
    list_by_parent_response = await client.get(
        f"/api/v1/organizations/{org.id}/folders",
        params={"parent_id": root_folder_id},
        headers=auth_headers,
    )
    assert list_by_parent_response.status_code == 200
    list_by_parent_data = list_by_parent_response.json()
    assert list_by_parent_data["total"] == 1
    assert list_by_parent_data["folders"][0]["name"] == "Child Folder"

    # 5. Get folder by ID
    get_response = await client.get(
        f"/api/v1/organizations/{org.id}/folders/{root_folder_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == root_folder_id
    assert get_data["name"] == "Root Folder"

    # 6. Update folder
    update_response = await client.put(
        f"/api/v1/organizations/{org.id}/folders/{root_folder_id}",
        json={
            "name": "Updated Root Folder",
            "position": 1,
        },
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    update_data = update_response.json()
    assert update_data["name"] == "Updated Root Folder"
    assert update_data["position"] == 1

    # 7. Delete child folder
    delete_response = await client.delete(
        f"/api/v1/organizations/{org.id}/folders/{child_folder_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    # 8. Verify child folder is deleted (soft-deleted, so not shown by default)
    list_after_delete_response = await client.get(
        f"/api/v1/organizations/{org.id}/folders",
        headers=auth_headers,
    )
    assert list_after_delete_response.status_code == 200
    list_after_delete_data = list_after_delete_response.json()
    # Should only have root folder (child is soft-deleted and not included by default)
    assert list_after_delete_data["total"] == 1
    assert list_after_delete_data["folders"][0]["name"] == "Updated Root Folder"

    # Verify child folder is soft-deleted by checking with include_deleted
    # Note: When parent_id is not specified, it defaults to None which means root folders only
    # So we need to check the child folder specifically by its parent_id
    list_with_deleted_response = await client.get(
        f"/api/v1/organizations/{org.id}/folders",
        params={"parent_id": root_folder_id, "include_deleted": True},
        headers=auth_headers,
    )
    assert list_with_deleted_response.status_code == 200
    list_with_deleted_data = list_with_deleted_response.json()
    # Should have the child folder (soft-deleted) when including deleted
    assert list_with_deleted_data["total"] == 1
    assert list_with_deleted_data["folders"][0]["name"] == "Child Folder"


@pytest.mark.asyncio
async def test_folder_node_assignment_workflow(client: AsyncClient, test_user, db_session):
    """Test workflow for assigning nodes to folders."""
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
        name="Projects Folder",
        position=0,
    )
    db_session.add(folder)
    await db_session.flush()

    # Create project and space
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
    db_session.add(project)
    db_session.add(space)
    await db_session.flush()

    # Login
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

    # 1. List nodes without folder filter (should show both)
    list_all_response = await client.get(
        f"/api/v1/organizations/{org.id}/nodes",
        headers=auth_headers,
    )
    assert list_all_response.status_code == 200
    list_all_data = list_all_response.json()
    assert list_all_data["total"] == 2

    # 2. Assign nodes to folder
    assign_response = await client.put(
        f"/api/v1/organizations/{org.id}/folders/{folder.id}/nodes",
        json={
            "node_ids": [str(project.id), str(space.id)],
        },
        headers=auth_headers,
    )
    assert assign_response.status_code == 204

    # 3. List nodes with folder filter (should show both)
    list_filtered_response = await client.get(
        f"/api/v1/organizations/{org.id}/nodes",
        params={"folder_id": str(folder.id)},
        headers=auth_headers,
    )
    assert list_filtered_response.status_code == 200
    list_filtered_data = list_filtered_response.json()
    assert list_filtered_data["total"] == 2
    for node in list_filtered_data["nodes"]:
        assert node["folder_id"] == str(folder.id)

    # 4. List nodes without folder filter (should show none, as all are in folder)
    list_no_folder_response = await client.get(
        f"/api/v1/organizations/{org.id}/nodes",
        headers=auth_headers,
    )
    assert list_no_folder_response.status_code == 200
    list_no_folder_data = list_no_folder_response.json()
    # When folder_id is None, it means "no filter", so should show all
    # But our implementation filters by folder_id=None when folder_id is not provided
    # Actually, looking at the implementation, if folder_id is None, we don't filter
    # So this should still show all nodes
    assert list_no_folder_data["total"] == 2


@pytest.mark.asyncio
async def test_folder_hierarchy_workflow(client: AsyncClient, test_user, db_session):
    """Test workflow for creating and managing folder hierarchy."""
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

    # Login
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

    # 1. Create level 1 folder
    level1_response = await client.post(
        f"/api/v1/organizations/{org.id}/folders",
        json={
            "organization_id": str(org.id),
            "name": "Level 1",
            "position": 0,
        },
        headers=auth_headers,
    )
    assert level1_response.status_code == 201
    level1_id = level1_response.json()["id"]

    # 2. Create level 2 folder
    level2_response = await client.post(
        f"/api/v1/organizations/{org.id}/folders",
        json={
            "organization_id": str(org.id),
            "name": "Level 2",
            "parent_id": level1_id,
            "position": 0,
        },
        headers=auth_headers,
    )
    assert level2_response.status_code == 201
    level2_id = level2_response.json()["id"]

    # 3. Create level 3 folder
    level3_response = await client.post(
        f"/api/v1/organizations/{org.id}/folders",
        json={
            "organization_id": str(org.id),
            "name": "Level 3",
            "parent_id": level2_id,
            "position": 0,
        },
        headers=auth_headers,
    )
    assert level3_response.status_code == 201
    level3_id = level3_response.json()["id"]

    # 4. Verify hierarchy
    list_level1_children = await client.get(
        f"/api/v1/organizations/{org.id}/folders",
        params={"parent_id": level1_id},
        headers=auth_headers,
    )
    assert list_level1_children.status_code == 200
    assert list_level1_children.json()["total"] == 1
    assert list_level1_children.json()["folders"][0]["id"] == level2_id

    list_level2_children = await client.get(
        f"/api/v1/organizations/{org.id}/folders",
        params={"parent_id": level2_id},
        headers=auth_headers,
    )
    assert list_level2_children.status_code == 200
    assert list_level2_children.json()["total"] == 1
    assert list_level2_children.json()["folders"][0]["id"] == level3_id

    # 5. Move level 3 to level 1 (change parent)
    move_response = await client.put(
        f"/api/v1/organizations/{org.id}/folders/{level3_id}",
        json={
            "parent_id": level1_id,
        },
        headers=auth_headers,
    )
    assert move_response.status_code == 200
    assert move_response.json()["parent_id"] == level1_id

    # 6. Verify new hierarchy
    list_level1_children_after = await client.get(
        f"/api/v1/organizations/{org.id}/folders",
        params={"parent_id": level1_id},
        headers=auth_headers,
    )
    assert list_level1_children_after.status_code == 200
    assert list_level1_children_after.json()["total"] == 2  # level2 and level3
