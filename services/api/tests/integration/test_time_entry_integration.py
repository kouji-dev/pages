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
