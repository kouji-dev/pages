"""Integration tests for time entry endpoints."""

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
async def test_create_time_entry_success(client: AsyncClient, test_user, db_session):
    """Test successful time entry creation."""
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

    # Create issue
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

    # Create time entry
    from datetime import date

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
    data = create_response.json()
    assert float(data["hours"]) == 2.5
    assert data["issue_id"] == str(issue.id)
    assert data["user_id"] == str(test_user.id)
    assert "id" in data


@pytest.mark.asyncio
async def test_list_time_entries_success(client: AsyncClient, test_user, db_session):
    """Test successfully listing time entries."""
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

    # List time entries
    list_response = await client.get(
        f"/api/v1/issues/{issue.id}/time-entries",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert "entries" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_create_time_entry_invalid_hours(client: AsyncClient, test_user, db_session):
    """Test creating time entry with invalid hours (negative or zero)."""
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

    # Try to create time entry with negative hours
    from datetime import date

    create_response = await client.post(
        f"/api/v1/issues/{issue.id}/time-entries",
        json={
            "hours": -1,
            "date": date.today().isoformat(),
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_time_entry_issue_not_found(client: AsyncClient, test_user, db_session):
    """Test creating time entry for non-existent issue."""
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

    # Try to create time entry for non-existent issue
    from datetime import date
    from uuid import uuid4

    create_response = await client.post(
        f"/api/v1/issues/{uuid4()}/time-entries",
        json={
            "hours": 2.5,
            "date": date.today().isoformat(),
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 404


async def _add_org_project_issue_and_login(client, test_user, db_session):
    """Create org, project, issue and return (issue, auth_headers)."""
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

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    return issue, auth_headers


@pytest.mark.asyncio
async def test_get_time_entry_success(client: AsyncClient, test_user, db_session):
    """Test get time entry by ID."""
    from datetime import date

    issue, auth_headers = await _add_org_project_issue_and_login(client, test_user, db_session)

    create_resp = await client.post(
        f"/api/v1/issues/{issue.id}/time-entries",
        json={
            "hours": 1.5,
            "date": date.today().isoformat(),
            "description": "Dev",
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    time_entry_id = create_resp.json()["id"]

    get_resp = await client.get(
        f"/api/v1/time-entries/{time_entry_id}",
        headers=auth_headers,
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == time_entry_id
    assert float(get_resp.json()["hours"]) == 1.5


@pytest.mark.asyncio
async def test_update_time_entry_success(client: AsyncClient, test_user, db_session):
    """Test update time entry."""
    from datetime import date

    issue, auth_headers = await _add_org_project_issue_and_login(client, test_user, db_session)

    create_resp = await client.post(
        f"/api/v1/issues/{issue.id}/time-entries",
        json={
            "hours": 1.0,
            "date": date.today().isoformat(),
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    time_entry_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/api/v1/time-entries/{time_entry_id}",
        json={
            "hours": 3.0,
            "date": date.today().isoformat(),
            "description": "Updated",
        },
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert float(update_resp.json()["hours"]) == 3.0
    assert update_resp.json()["description"] == "Updated"


@pytest.mark.asyncio
async def test_delete_time_entry_success(client: AsyncClient, test_user, db_session):
    """Test delete time entry."""
    from datetime import date

    issue, auth_headers = await _add_org_project_issue_and_login(client, test_user, db_session)

    create_resp = await client.post(
        f"/api/v1/issues/{issue.id}/time-entries",
        json={
            "hours": 1.0,
            "date": date.today().isoformat(),
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    time_entry_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/api/v1/time-entries/{time_entry_id}",
        headers=auth_headers,
    )
    assert delete_resp.status_code == 204

    get_resp = await client.get(
        f"/api/v1/time-entries/{time_entry_id}",
        headers=auth_headers,
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_time_summary_success(client: AsyncClient, test_user, db_session):
    """Test get time summary for an issue."""
    from datetime import date

    issue, auth_headers = await _add_org_project_issue_and_login(client, test_user, db_session)

    await client.post(
        f"/api/v1/issues/{issue.id}/time-entries",
        json={
            "hours": 2.0,
            "date": date.today().isoformat(),
        },
        headers=auth_headers,
    )
    await client.post(
        f"/api/v1/issues/{issue.id}/time-entries",
        json={
            "hours": 1.5,
            "date": date.today().isoformat(),
        },
        headers=auth_headers,
    )

    summary_resp = await client.get(
        f"/api/v1/issues/{issue.id}/time-summary",
        headers=auth_headers,
    )
    assert summary_resp.status_code == 200
    data = summary_resp.json()
    assert "total_hours" in data
    assert float(data["total_hours"]) == 3.5


@pytest.mark.asyncio
async def test_get_time_entry_not_found(client: AsyncClient, test_user):
    """Test get time entry returns 404 when not found."""
    from uuid import uuid4

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    resp = await client.get(
        f"/api/v1/time-entries/{uuid4()}",
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_time_entry_not_found(client: AsyncClient, test_user):
    """Test update time entry returns 404 when not found."""
    from datetime import date
    from uuid import uuid4

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    resp = await client.put(
        f"/api/v1/time-entries/{uuid4()}",
        json={"hours": 1.0, "date": date.today().isoformat()},
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_time_entry_not_found(client: AsyncClient, test_user):
    """Test delete time entry returns 404 when not found."""
    from uuid import uuid4

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    resp = await client.delete(
        f"/api/v1/time-entries/{uuid4()}",
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_time_summary_issue_not_found(client: AsyncClient, test_user):
    """Test get time summary returns 404 when issue not found."""
    from uuid import uuid4

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    resp = await client.get(
        f"/api/v1/issues/{uuid4()}/time-summary",
        headers=auth_headers,
    )
    assert resp.status_code == 404
