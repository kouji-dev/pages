"""Integration tests for whiteboard endpoints."""

import json

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    SpaceModel,
    WhiteboardModel,
)


@pytest.mark.asyncio
async def test_create_whiteboard_success(client: AsyncClient, test_user, db_session):
    """Test successful whiteboard creation."""
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

    # Create whiteboard
    create_response = await client.post(
        "/api/v1/whiteboards/",
        json={
            "space_id": str(space.id),
            "name": "My Whiteboard",
            "data": {"nodes": [], "edges": []},
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "My Whiteboard"
    assert data["space_id"] == str(space.id)
    assert "id" in data


@pytest.mark.asyncio
async def test_get_whiteboard_success(client: AsyncClient, test_user, db_session):
    """Test successful whiteboard retrieval."""
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

    # Create whiteboard
    whiteboard = WhiteboardModel(
        space_id=space.id,
        name="Test Whiteboard",
        data=json.dumps({"nodes": [{"id": "1", "type": "text"}], "edges": []}),
        created_by=test_user.id,
    )
    db_session.add(whiteboard)
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

    # Get whiteboard
    get_response = await client.get(f"/api/v1/whiteboards/{whiteboard.id}", headers=auth_headers)

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(whiteboard.id)
    assert data["name"] == "Test Whiteboard"
    assert "data" in data


@pytest.mark.asyncio
async def test_list_whiteboards_success(client: AsyncClient, test_user, db_session):
    """Test successful whiteboard listing."""
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

    # Create whiteboards
    whiteboard1 = WhiteboardModel(
        space_id=space.id,
        name="Whiteboard 1",
        data=json.dumps({"nodes": [], "edges": []}),
        created_by=test_user.id,
    )
    whiteboard2 = WhiteboardModel(
        space_id=space.id,
        name="Whiteboard 2",
        data=json.dumps({"nodes": [], "edges": []}),
        created_by=test_user.id,
    )
    db_session.add(whiteboard1)
    db_session.add(whiteboard2)
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

    # List whiteboards
    list_response = await client.get(f"/api/v1/spaces/{space.id}/whiteboards", headers=auth_headers)

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["whiteboards"]) == 2
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_update_whiteboard_success(client: AsyncClient, test_user, db_session):
    """Test successful whiteboard update."""
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

    # Create whiteboard
    whiteboard = WhiteboardModel(
        space_id=space.id,
        name="Test Whiteboard",
        data=json.dumps({"nodes": [], "edges": []}),
        created_by=test_user.id,
    )
    db_session.add(whiteboard)
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

    # Update whiteboard
    update_response = await client.put(
        f"/api/v1/whiteboards/{whiteboard.id}",
        json={
            "name": "Updated Whiteboard",
            "data": {"nodes": [{"id": "1"}], "edges": []},
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Whiteboard"
    assert "data" in data


@pytest.mark.asyncio
async def test_delete_whiteboard_success(client: AsyncClient, test_user, db_session):
    """Test successful whiteboard deletion."""
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

    # Create whiteboard
    whiteboard = WhiteboardModel(
        space_id=space.id,
        name="Test Whiteboard",
        data=json.dumps({"nodes": [], "edges": []}),
        created_by=test_user.id,
    )
    db_session.add(whiteboard)
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

    # Delete whiteboard
    delete_response = await client.delete(
        f"/api/v1/whiteboards/{whiteboard.id}", headers=auth_headers
    )

    assert delete_response.status_code == 204

    # Verify whiteboard is soft-deleted
    get_response = await client.get(f"/api/v1/whiteboards/{whiteboard.id}", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_whiteboard_not_found(client: AsyncClient, test_user, db_session):
    """Test getting non-existent whiteboard."""
    from uuid import uuid4

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

    # Get non-existent whiteboard
    get_response = await client.get(f"/api/v1/whiteboards/{uuid4()}", headers=auth_headers)

    assert get_response.status_code == 404
