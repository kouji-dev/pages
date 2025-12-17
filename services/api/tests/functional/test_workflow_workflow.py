"""Functional tests for workflow management workflow."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    ProjectMemberModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_workflow_management_workflow(client: AsyncClient, test_user, db_session):
    """Test complete workflow management workflow."""
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

    # 1. Create workflow
    create_response = await client.post(
        f"/api/v1/projects/{project.id}/workflows",
        json={
            "name": "Development Workflow",
            "is_default": True,
            "statuses": [
                {"name": "To Do", "order": 0, "is_initial": True, "is_final": False},
                {"name": "In Progress", "order": 1, "is_initial": False, "is_final": False},
                {"name": "Done", "order": 2, "is_initial": False, "is_final": True},
            ],
            "transitions": [],
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    workflow_data = create_response.json()
    workflow_id = workflow_data["id"]

    # 2. Get workflow
    get_response = await client.get(
        f"/api/v1/workflows/{workflow_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Development Workflow"

    # 3. List workflows
    list_response = await client.get(
        f"/api/v1/projects/{project.id}/workflows",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 1

    # 4. Update workflow
    update_response = await client.put(
        f"/api/v1/workflows/{workflow_id}",
        json={"name": "Updated Workflow"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Workflow"

    # 5. Delete workflow
    delete_response = await client.delete(
        f"/api/v1/workflows/{workflow_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204
