"""Integration tests for node endpoints."""

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
async def test_list_nodes_success(client: AsyncClient, test_user, db_session):
    """Test successful node listing."""
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

    # List nodes
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/nodes",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 2
    assert len(data["nodes"]) == 2
    node_types = [node["type"] for node in data["nodes"]]
    assert "project" in node_types
    assert "space" in node_types


@pytest.mark.asyncio
async def test_list_nodes_with_folder_filter(client: AsyncClient, test_user, db_session):
    """Test node listing with folder filter."""
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

    # List nodes in folder
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/nodes",
        params={"folder_id": str(folder.id)},
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 1
    assert len(data["nodes"]) == 1
    assert data["nodes"][0]["type"] == "project"
    assert data["nodes"][0]["folder_id"] == str(folder.id)


@pytest.mark.asyncio
async def test_list_nodes_empty(client: AsyncClient, test_user, db_session):
    """Test node listing with no nodes."""
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

    # List nodes
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/nodes",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 0
    assert len(data["nodes"]) == 0


@pytest.mark.asyncio
async def test_list_nodes_requires_auth(client: AsyncClient):
    """Test node listing requires authentication."""
    response = await client.get(f"/api/v1/organizations/{uuid4()}/nodes")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_nodes_requires_org_membership(client: AsyncClient, test_user, db_session):
    """Test node listing requires organization membership."""
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

    # Try to list nodes
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/nodes",
        headers=auth_headers,
    )

    assert list_response.status_code == 403

