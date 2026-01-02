"""Integration tests for backlog endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    IssueModel,
    OrganizationModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_list_backlog_success(client: AsyncClient, test_user, db_session):
    """Test successful backlog listing."""
    # Create organization and project
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    # Create issues (not in sprint = in backlog)
    issue1 = IssueModel(
        project_id=project.id,
        title="Backlog Issue 1",
        issue_number=1,
        type="task",
        status="todo",
        priority="medium",
        backlog_order=0,
    )
    issue2 = IssueModel(
        project_id=project.id,
        title="Backlog Issue 2",
        issue_number=2,
        type="bug",
        status="todo",
        priority="high",
        backlog_order=1,
    )
    db_session.add(issue1)
    db_session.add(issue2)
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

    # List backlog
    list_response = await client.get(
        f"/api/v1/projects/{project.id}/backlog",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 2
    assert len(data["issues"]) == 2
    issue_ids = [issue["id"] for issue in data["issues"]]
    assert str(issue1.id) in issue_ids
    assert str(issue2.id) in issue_ids
    assert data["page"] == 1
    assert data["limit"] == 20


@pytest.mark.asyncio
async def test_list_backlog_with_filters(client: AsyncClient, test_user, db_session):
    """Test backlog listing with filters."""
    # Create organization and project
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    # Create issues
    issue1 = IssueModel(
        project_id=project.id,
        title="Task Issue",
        issue_number=1,
        type="task",
        status="todo",
        priority="medium",
        backlog_order=0,
    )
    issue2 = IssueModel(
        project_id=project.id,
        title="Bug Issue",
        issue_number=2,
        type="bug",
        status="todo",
        priority="high",
        backlog_order=1,
    )
    db_session.add(issue1)
    db_session.add(issue2)
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

    # Filter by type
    filtered_response = await client.get(
        f"/api/v1/projects/{project.id}/backlog",
        params={"type_filter": "task"},
        headers=auth_headers,
    )
    assert filtered_response.status_code == 200
    filtered_data = filtered_response.json()
    assert filtered_data["total"] == 1
    issue_ids = [issue["id"] for issue in filtered_data["issues"]]
    assert str(issue1.id) in issue_ids

    # Filter by priority
    priority_response = await client.get(
        f"/api/v1/projects/{project.id}/backlog",
        params={"priority_filter": "high"},
        headers=auth_headers,
    )
    assert priority_response.status_code == 200
    priority_data = priority_response.json()
    assert priority_data["total"] == 1
    assert str(issue2.id) in priority_data["issues"]


@pytest.mark.asyncio
async def test_list_backlog_requires_auth(client: AsyncClient, db_session):
    """Test backlog listing requires authentication."""
    # Create project
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    response = await client.get(f"/api/v1/projects/{project.id}/backlog")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_backlog_project_not_found(client: AsyncClient, test_user):
    """Test backlog listing when project not found."""
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

    # Try to list backlog for non-existent project
    response = await client.get(
        f"/api/v1/projects/{uuid4()}/backlog",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_prioritize_backlog_success(client: AsyncClient, test_user, db_session):
    """Test successful backlog prioritization."""
    # Create organization and project
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    # Create issues
    issue1 = IssueModel(
        project_id=project.id,
        title="Issue 1",
        issue_number=1,
        type="task",
        status="todo",
        priority="medium",
    )
    issue2 = IssueModel(
        project_id=project.id,
        title="Issue 2",
        issue_number=2,
        type="task",
        status="todo",
        priority="medium",
    )
    db_session.add(issue1)
    db_session.add(issue2)
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

    # Prioritize backlog
    prioritize_response = await client.put(
        f"/api/v1/projects/{project.id}/backlog/prioritize",
        json={"issue_ids": [str(issue2.id), str(issue1.id)]},  # Issue 2 first
        headers=auth_headers,
    )
    assert prioritize_response.status_code == 204

    # Verify order in backlog listing
    backlog_response = await client.get(
        f"/api/v1/projects/{project.id}/backlog",
        params={"sort_by": "backlog_order"},
        headers=auth_headers,
    )
    assert backlog_response.status_code == 200
    backlog_data = backlog_response.json()
    assert backlog_data["issues"][0]["id"] == str(issue2.id)  # First in list
    assert backlog_data["issues"][1]["id"] == str(issue1.id)  # Second


@pytest.mark.asyncio
async def test_reorder_backlog_issue_success(client: AsyncClient, test_user, db_session):
    """Test successful backlog issue reordering."""
    # Create organization and project
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    # Create issues with initial order
    issue1 = IssueModel(
        project_id=project.id,
        title="Issue 1",
        issue_number=1,
        type="task",
        status="todo",
        priority="medium",
        backlog_order=0,
    )
    issue2 = IssueModel(
        project_id=project.id,
        title="Issue 2",
        issue_number=2,
        type="task",
        status="todo",
        priority="medium",
        backlog_order=1,
    )
    db_session.add(issue1)
    db_session.add(issue2)
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

    # Reorder issue2 to position 0
    reorder_response = await client.put(
        f"/api/v1/projects/{project.id}/backlog/issues/{issue2.id}/reorder",
        json={"position": 0},
        headers=auth_headers,
    )
    assert reorder_response.status_code == 204

    # Verify new order
    backlog_response = await client.get(
        f"/api/v1/projects/{project.id}/backlog",
        params={"sort_by": "backlog_order"},
        headers=auth_headers,
    )
    assert backlog_response.status_code == 200
    backlog_data = backlog_response.json()
    assert backlog_data["issues"][0]["id"] == str(issue2.id)  # Now first
