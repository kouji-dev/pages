"""Integration tests for dashboard endpoints."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    ProjectMemberModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_create_dashboard_success(client: AsyncClient, test_user, db_session):
    """Test successful dashboard creation."""
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

    # Create dashboard
    create_response = await client.post(
        "/api/v1/dashboards",
        json={
            "name": "Test Dashboard",
            "project_id": str(project.id),
            "widgets": [
                {
                    "type": "issue_status_breakdown",
                    "config": {},
                    "position": 0,
                }
            ],
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "Test Dashboard"
    assert data["project_id"] == str(project.id)
    assert len(data["widgets"]) == 1
    assert "id" in data


@pytest.mark.asyncio
async def test_list_dashboards_success(client: AsyncClient, test_user, db_session):
    """Test successfully listing dashboards."""
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

    # List dashboards
    list_response = await client.get(
        "/api/v1/dashboards",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert "dashboards" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_dashboard_success(client: AsyncClient, test_user, db_session):
    """Test successfully getting a dashboard by ID."""
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

    # Create dashboard
    create_response = await client.post(
        "/api/v1/dashboards",
        json={
            "name": "Test Dashboard",
            "project_id": str(project.id),
            "widgets": [],
        },
        headers=auth_headers,
    )
    dashboard_id = create_response.json()["id"]

    # Get dashboard
    get_response = await client.get(
        f"/api/v1/dashboards/{dashboard_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == dashboard_id
    assert data["name"] == "Test Dashboard"


@pytest.mark.asyncio
async def test_get_dashboard_not_found(client: AsyncClient, test_user, db_session):
    """Test getting a non-existent dashboard returns 404."""
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

    # Get non-existent dashboard
    from uuid import uuid4

    get_response = await client.get(
        f"/api/v1/dashboards/{uuid4()}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_create_dashboard_invalid_widget_type(client: AsyncClient, test_user, db_session):
    """Test creating dashboard with invalid widget type."""
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

    # Try to create dashboard with invalid widget type
    create_response = await client.post(
        "/api/v1/dashboards",
        json={
            "name": "Test Dashboard",
            "project_id": str(project.id),
            "widgets": [
                {
                    "type": "invalid_widget_type",
                    "config": {},
                    "position": 0,
                }
            ],
        },
        headers=auth_headers,
    )

    assert create_response.status_code in [400, 422]  # Validation error
