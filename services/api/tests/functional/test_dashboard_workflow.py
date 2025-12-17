"""Functional tests for dashboard management workflow."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    ProjectMemberModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_dashboard_management_workflow(client: AsyncClient, test_user, db_session):
    """Test complete dashboard management workflow."""
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

    # 1. Create dashboard
    create_response = await client.post(
        "/api/v1/dashboards",
        json={
            "name": "My Dashboard",
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
    dashboard_data = create_response.json()
    dashboard_id = dashboard_data["id"]

    # 2. Get dashboard
    get_response = await client.get(
        f"/api/v1/dashboards/{dashboard_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "My Dashboard"

    # 3. List dashboards
    list_response = await client.get(
        "/api/v1/dashboards",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 1

    # 4. Update dashboard
    update_response = await client.put(
        f"/api/v1/dashboards/{dashboard_id}",
        json={"name": "Updated Dashboard"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Dashboard"

    # 5. Delete dashboard
    delete_response = await client.delete(
        f"/api/v1/dashboards/{dashboard_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204
