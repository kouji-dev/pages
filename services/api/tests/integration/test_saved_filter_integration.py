"""Integration tests for saved filter endpoints."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    ProjectMemberModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_create_saved_filter_success(client: AsyncClient, test_user, db_session):
    """Test successful saved filter creation."""
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

    # Create project
    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    # Add user as project member
    project_member = ProjectMemberModel(
        project_id=project.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(project_member)
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

    # Create saved filter
    create_response = await client.post(
        "/api/v1/saved-filters",
        json={
            "name": "My Filter",
            "project_id": str(project.id),
            "filter_criteria": {
                "status": "todo",
                "priority": "high",
            },
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "My Filter"
    assert data["filter_criteria"] == {"status": "todo", "priority": "high"}
    assert "id" in data


@pytest.mark.asyncio
async def test_list_saved_filters_success(client: AsyncClient, test_user, db_session):
    """Test successfully listing saved filters."""
    # Setup same as above
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

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
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # List saved filters
    list_response = await client.get(
        "/api/v1/saved-filters",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert "filters" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_saved_filter_success(client: AsyncClient, test_user, db_session):
    """Test successfully getting a saved filter by ID."""
    # Setup
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    project_member = ProjectMemberModel(
        project_id=project.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(project_member)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create saved filter
    create_response = await client.post(
        "/api/v1/saved-filters",
        json={
            "name": "My Filter",
            "project_id": str(project.id),
            "filter_criteria": {
                "status": "todo",
                "priority": "high",
            },
        },
        headers=auth_headers,
    )
    filter_id = create_response.json()["id"]

    # Get saved filter
    get_response = await client.get(
        f"/api/v1/saved-filters/{filter_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == filter_id
    assert data["name"] == "My Filter"


@pytest.mark.asyncio
async def test_get_saved_filter_not_found(client: AsyncClient, test_user, db_session):
    """Test getting a non-existent saved filter returns 404."""
    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Get non-existent saved filter
    from uuid import uuid4

    get_response = await client.get(
        f"/api/v1/saved-filters/{uuid4()}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_update_saved_filter_success(client: AsyncClient, test_user, db_session):
    """Test successfully updating a saved filter."""
    # Setup
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    project_member = ProjectMemberModel(
        project_id=project.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(project_member)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create saved filter
    create_response = await client.post(
        "/api/v1/saved-filters",
        json={
            "name": "My Filter",
            "project_id": str(project.id),
            "filter_criteria": {
                "status": "todo",
            },
        },
        headers=auth_headers,
    )
    filter_id = create_response.json()["id"]

    # Update saved filter
    update_response = await client.put(
        f"/api/v1/saved-filters/{filter_id}",
        json={
            "name": "Updated Filter",
            "filter_criteria": {
                "status": "in_progress",
            },
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Filter"
    assert data["filter_criteria"] == {"status": "in_progress"}


@pytest.mark.asyncio
async def test_delete_saved_filter_success(client: AsyncClient, test_user, db_session):
    """Test successfully deleting a saved filter."""
    # Setup
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    project_member = ProjectMemberModel(
        project_id=project.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(project_member)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create saved filter
    create_response = await client.post(
        "/api/v1/saved-filters",
        json={
            "name": "My Filter",
            "project_id": str(project.id),
            "filter_criteria": {
                "status": "todo",
            },
        },
        headers=auth_headers,
    )
    filter_id = create_response.json()["id"]

    # Delete saved filter
    delete_response = await client.delete(
        f"/api/v1/saved-filters/{filter_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    # Verify saved filter is deleted
    get_response = await client.get(
        f"/api/v1/saved-filters/{filter_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404
