"""Functional tests for saved filter management workflow."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    ProjectMemberModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_saved_filter_management_workflow(client: AsyncClient, test_user, db_session):
    """Test complete saved filter management workflow."""
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

    # 1. Create saved filter
    create_response = await client.post(
        "/api/v1/saved-filters",
        json={
            "name": "High Priority Issues",
            "project_id": str(project.id),
            "filter_criteria": {
                "priority": "high",
                "status": "todo",
            },
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    filter_data = create_response.json()
    filter_id = filter_data["id"]

    # 2. Get saved filter
    get_response = await client.get(
        f"/api/v1/saved-filters/{filter_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "High Priority Issues"

    # 3. List saved filters
    list_response = await client.get(
        "/api/v1/saved-filters",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 1

    # 4. Update saved filter
    update_response = await client.put(
        f"/api/v1/saved-filters/{filter_id}",
        json={"name": "Updated Filter"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Filter"

    # 5. Delete saved filter
    delete_response = await client.delete(
        f"/api/v1/saved-filters/{filter_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204
