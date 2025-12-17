"""Functional tests for time tracking workflow."""

from datetime import date

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    IssueModel,
    OrganizationMemberModel,
    OrganizationModel,
    ProjectMemberModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_time_tracking_workflow(client: AsyncClient, test_user, db_session):
    """Test complete time tracking workflow."""
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

    issue = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Test Issue",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    db_session.add(issue)
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

    # 1. Create time entry
    create_response = await client.post(
        f"/api/v1/issues/{issue.id}/time-entries",
        json={
            "hours": 2.5,
            "date": date.today().isoformat(),
            "description": "Worked on feature",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    entry_data = create_response.json()
    entry_id = entry_data["id"]

    # 2. Get time entry
    get_response = await client.get(
        f"/api/v1/time-entries/{entry_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
    assert float(get_response.json()["hours"]) == 2.5

    # 3. List time entries
    list_response = await client.get(
        f"/api/v1/issues/{issue.id}/time-entries",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 1

    # 4. Get time summary
    summary_response = await client.get(
        f"/api/v1/issues/{issue.id}/time-summary",
        headers=auth_headers,
    )
    assert summary_response.status_code == 200
    assert "total_hours" in summary_response.json()

    # 5. Update time entry
    update_response = await client.put(
        f"/api/v1/time-entries/{entry_id}",
        json={"hours": 3.0, "date": date.today().isoformat()},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert float(update_response.json()["hours"]) == 3.0

    # 6. Delete time entry
    delete_response = await client.delete(
        f"/api/v1/time-entries/{entry_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204
