"""Integration tests for workflow endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    ProjectMemberModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_create_workflow_success(client: AsyncClient, test_user, db_session):
    """Test successful workflow creation."""
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

    # Create workflow
    create_response = await client.post(
        f"/api/v1/projects/{project.id}/workflows",
        json={
            "name": "Test Workflow",
            "is_default": True,
            "statuses": [
                {
                    "name": "To Do",
                    "order": 0,
                    "is_initial": True,
                    "is_final": False,
                },
                {
                    "name": "In Progress",
                    "order": 1,
                    "is_initial": False,
                    "is_final": False,
                },
                {
                    "name": "Done",
                    "order": 2,
                    "is_initial": False,
                    "is_final": True,
                },
            ],
            "transitions": [
                {
                    "from_status_id": "placeholder",
                    "to_status_id": "placeholder",
                    "name": "Start",
                },
            ],
        },
        headers=auth_headers,
    )

    # Note: The transitions will need status IDs which are generated
    # For now, test without transitions
    create_response = await client.post(
        f"/api/v1/projects/{project.id}/workflows",
        json={
            "name": "Test Workflow",
            "is_default": True,
            "statuses": [
                {
                    "name": "To Do",
                    "order": 0,
                    "is_initial": True,
                    "is_final": False,
                },
                {
                    "name": "Done",
                    "order": 1,
                    "is_initial": False,
                    "is_final": True,
                },
            ],
            "transitions": [],
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "Test Workflow"
    assert data["is_default"] is True
    assert len(data["statuses"]) == 2
    assert "id" in data


@pytest.mark.asyncio
async def test_list_workflows_success(client: AsyncClient, test_user, db_session):
    """Test successfully listing workflows."""
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

    # List workflows
    list_response = await client.get(
        f"/api/v1/projects/{project.id}/workflows",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert "workflows" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_workflow_success(client: AsyncClient, test_user, db_session):
    """Test successfully getting a workflow by ID."""
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

    # Create workflow
    create_response = await client.post(
        f"/api/v1/projects/{project.id}/workflows",
        json={
            "name": "Test Workflow",
            "is_default": True,
            "statuses": [
                {
                    "name": "To Do",
                    "order": 0,
                    "is_initial": True,
                    "is_final": False,
                },
                {
                    "name": "Done",
                    "order": 1,
                    "is_initial": False,
                    "is_final": True,
                },
            ],
            "transitions": [],
        },
        headers=auth_headers,
    )
    workflow_id = create_response.json()["id"]

    # Get workflow
    get_response = await client.get(
        f"/api/v1/workflows/{workflow_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == workflow_id
    assert data["name"] == "Test Workflow"


@pytest.mark.asyncio
async def test_update_workflow_success(client: AsyncClient, test_user, db_session):
    """Test successfully updating a workflow."""
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

    # Create workflow
    create_response = await client.post(
        f"/api/v1/projects/{project.id}/workflows",
        json={
            "name": "Test Workflow",
            "is_default": True,
            "statuses": [
                {
                    "name": "To Do",
                    "order": 0,
                    "is_initial": True,
                    "is_final": False,
                },
                {
                    "name": "Done",
                    "order": 1,
                    "is_initial": False,
                    "is_final": True,
                },
            ],
            "transitions": [],
        },
        headers=auth_headers,
    )
    workflow_id = create_response.json()["id"]

    # Update workflow
    update_response = await client.put(
        f"/api/v1/workflows/{workflow_id}",
        json={
            "name": "Updated Workflow",
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Workflow"


@pytest.mark.asyncio
async def test_delete_workflow_success(client: AsyncClient, test_user, db_session):
    """Test successfully deleting a workflow."""
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

    # Create workflow
    create_response = await client.post(
        f"/api/v1/projects/{project.id}/workflows",
        json={
            "name": "Test Workflow",
            "is_default": True,
            "statuses": [
                {
                    "name": "To Do",
                    "order": 0,
                    "is_initial": True,
                    "is_final": False,
                },
                {
                    "name": "Done",
                    "order": 1,
                    "is_initial": False,
                    "is_final": True,
                },
            ],
            "transitions": [],
        },
        headers=auth_headers,
    )
    workflow_id = create_response.json()["id"]

    # Delete workflow
    delete_response = await client.delete(
        f"/api/v1/workflows/{workflow_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    # Verify workflow is deleted
    get_response = await client.get(
        f"/api/v1/workflows/{workflow_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_workflow_not_found(client: AsyncClient, test_user, db_session):
    """Test getting a non-existent workflow returns 404."""
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

    # Get non-existent workflow

    get_response = await client.get(
        f"/api/v1/workflows/{uuid4()}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404
