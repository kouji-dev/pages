"""Functional tests for node workflows."""

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
async def test_node_filtering_workflow(client: AsyncClient, test_user, db_session):
    """Test workflow for filtering nodes by folder."""
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

    # Create projects and spaces
    project1 = ProjectModel(
        organization_id=org.id,
        name="Project 1",
        key="PROJ1",
        folder_id=folder1.id,
    )
    project2 = ProjectModel(
        organization_id=org.id,
        name="Project 2",
        key="PROJ2",
        folder_id=folder2.id,
    )
    project3 = ProjectModel(
        organization_id=org.id,
        name="Project 3",
        key="PROJ3",
        folder_id=None,  # No folder
    )
    space1 = SpaceModel(
        organization_id=org.id,
        name="Space 1",
        key="SPACE1",
        folder_id=folder1.id,
    )
    space2 = SpaceModel(
        organization_id=org.id,
        name="Space 2",
        key="SPACE2",
        folder_id=None,  # No folder
    )
    db_session.add_all([project1, project2, project3, space1, space2])
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

    # 1. List all nodes (should show all 5)
    list_all_response = await client.get(
        f"/api/v1/organizations/{org.id}/nodes",
        headers=auth_headers,
    )
    assert list_all_response.status_code == 200
    list_all_data = list_all_response.json()
    assert list_all_data["total"] == 5

    # 2. List nodes in folder1 (should show project1 and space1)
    list_folder1_response = await client.get(
        f"/api/v1/organizations/{org.id}/nodes",
        params={"folder_id": str(folder1.id)},
        headers=auth_headers,
    )
    assert list_folder1_response.status_code == 200
    list_folder1_data = list_folder1_response.json()
    assert list_folder1_data["total"] == 2
    node_names = [node["name"] for node in list_folder1_data["nodes"]]
    assert "Project 1" in node_names
    assert "Space 1" in node_names

    # 3. List nodes in folder2 (should show project2 only)
    list_folder2_response = await client.get(
        f"/api/v1/organizations/{org.id}/nodes",
        params={"folder_id": str(folder2.id)},
        headers=auth_headers,
    )
    assert list_folder2_response.status_code == 200
    list_folder2_data = list_folder2_response.json()
    assert list_folder2_data["total"] == 1
    assert list_folder2_data["nodes"][0]["name"] == "Project 2"

    # 4. Verify folder_id in response
    for node in list_folder1_data["nodes"]:
        assert node["folder_id"] == str(folder1.id)


@pytest.mark.asyncio
async def test_node_organization_isolation_workflow(
    client: AsyncClient, test_user, db_session
):
    """Test that nodes are properly isolated by organization."""
    # Create two organizations
    org1 = OrganizationModel(name="Org 1", slug="org-1")
    org2 = OrganizationModel(name="Org 2", slug="org-2")
    db_session.add(org1)
    db_session.add(org2)
    await db_session.flush()

    # Add user as member of both
    org1_member = OrganizationMemberModel(
        organization_id=org1.id,
        user_id=test_user.id,
        role="member",
    )
    org2_member = OrganizationMemberModel(
        organization_id=org2.id,
        user_id=test_user.id,
        role="member",
    )
    db_session.add(org1_member)
    db_session.add(org2_member)
    await db_session.flush()

    # Create projects in each organization
    project1 = ProjectModel(
        organization_id=org1.id,
        name="Org1 Project",
        key="ORG1",
    )
    project2 = ProjectModel(
        organization_id=org2.id,
        name="Org2 Project",
        key="ORG2",
    )
    db_session.add(project1)
    db_session.add(project2)
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

    # List nodes in org1 (should only show org1 project)
    list_org1_response = await client.get(
        f"/api/v1/organizations/{org1.id}/nodes",
        headers=auth_headers,
    )
    assert list_org1_response.status_code == 200
    list_org1_data = list_org1_response.json()
    assert list_org1_data["total"] == 1
    assert list_org1_data["nodes"][0]["name"] == "Org1 Project"

    # List nodes in org2 (should only show org2 project)
    list_org2_response = await client.get(
        f"/api/v1/organizations/{org2.id}/nodes",
        headers=auth_headers,
    )
    assert list_org2_response.status_code == 200
    list_org2_data = list_org2_response.json()
    assert list_org2_data["total"] == 1
    assert list_org2_data["nodes"][0]["name"] == "Org2 Project"

