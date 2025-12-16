"""Integration tests for sprint endpoints."""

from datetime import date
from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationModel,
    ProjectModel,
    SprintModel,
)


@pytest.mark.asyncio
async def test_create_sprint_success(client: AsyncClient, test_user, db_session):
    """Test successful sprint creation."""
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

    # Create sprint
    create_response = await client.post(
        f"/api/v1/projects/{project.id}/sprints",
        json={
            "name": "Sprint 1",
            "goal": "Test goal",
            "start_date": "2024-01-01",
            "end_date": "2024-01-14",
            "status": "planned",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "Sprint 1"
    assert data["goal"] == "Test goal"
    assert data["start_date"] == "2024-01-01"
    assert data["end_date"] == "2024-01-14"
    assert data["status"] == "planned"
    assert data["project_id"] == str(project.id)
    assert "id" in data


@pytest.mark.asyncio
async def test_create_sprint_requires_auth(client: AsyncClient, db_session):
    """Test sprint creation requires authentication."""
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

    response = await client.post(
        f"/api/v1/projects/{project.id}/sprints",
        json={"name": "Sprint 1"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_sprint_project_not_found(client: AsyncClient, test_user):
    """Test sprint creation when project not found."""
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

    # Try to create sprint for non-existent project
    response = await client.post(
        f"/api/v1/projects/{uuid4()}/sprints",
        json={"name": "Sprint 1"},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_sprint_success(client: AsyncClient, test_user, db_session):
    """Test successful sprint retrieval."""
    # Create organization, project, and sprint
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

    sprint = SprintModel(
        project_id=project.id,
        name="Sprint 1",
        goal="Test goal",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 14),
        status="planned",
    )
    db_session.add(sprint)
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

    # Get sprint
    get_response = await client.get(
        f"/api/v1/sprints/{sprint.id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(sprint.id)
    assert data["name"] == "Sprint 1"
    assert data["goal"] == "Test goal"
    assert data["issues"] == []


@pytest.mark.asyncio
async def test_get_sprint_not_found(client: AsyncClient, test_user):
    """Test sprint retrieval when sprint not found."""
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

    # Try to get non-existent sprint
    response = await client.get(
        f"/api/v1/sprints/{uuid4()}",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_sprints_success(client: AsyncClient, test_user, db_session):
    """Test successful sprint listing."""
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

    # Create sprints
    sprint1 = SprintModel(
        project_id=project.id,
        name="Sprint 1",
        status="planned",
    )
    sprint2 = SprintModel(
        project_id=project.id,
        name="Sprint 2",
        status="active",
    )
    db_session.add(sprint1)
    db_session.add(sprint2)
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

    # List sprints
    list_response = await client.get(
        f"/api/v1/projects/{project.id}/sprints",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 2
    assert len(data["sprints"]) == 2
    assert data["page"] == 1
    assert data["limit"] == 20


@pytest.mark.asyncio
async def test_list_sprints_with_status_filter(client: AsyncClient, test_user, db_session):
    """Test sprint listing with status filter."""
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

    # Create sprints
    sprint1 = SprintModel(
        project_id=project.id,
        name="Sprint 1",
        status="planned",
    )
    sprint2 = SprintModel(
        project_id=project.id,
        name="Sprint 2",
        status="active",
    )
    db_session.add(sprint1)
    db_session.add(sprint2)
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

    # List sprints with status filter
    list_response = await client.get(
        f"/api/v1/projects/{project.id}/sprints",
        params={"status_filter": "active"},
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 1
    assert len(data["sprints"]) == 1
    assert data["sprints"][0]["status"] == "active"


@pytest.mark.asyncio
async def test_update_sprint_success(client: AsyncClient, test_user, db_session):
    """Test successful sprint update."""
    # Create organization, project, and sprint
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

    sprint = SprintModel(
        project_id=project.id,
        name="Sprint 1",
        status="planned",
    )
    db_session.add(sprint)
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

    # Update sprint
    update_response = await client.put(
        f"/api/v1/sprints/{sprint.id}",
        json={
            "name": "Updated Sprint Name",
            "goal": "Updated goal",
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Sprint Name"
    assert data["goal"] == "Updated goal"


@pytest.mark.asyncio
async def test_delete_sprint_success(client: AsyncClient, test_user, db_session):
    """Test successful sprint deletion."""
    # Create organization, project, and sprint
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

    sprint = SprintModel(
        project_id=project.id,
        name="Sprint 1",
        status="planned",
    )
    db_session.add(sprint)
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

    # Delete sprint
    delete_response = await client.delete(
        f"/api/v1/sprints/{sprint.id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    # Verify sprint is deleted
    get_response = await client.get(
        f"/api/v1/sprints/{sprint.id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_sprint_metrics_success(client: AsyncClient, test_user, db_session):
    """Test successful sprint metrics retrieval."""
    from datetime import date

    from src.infrastructure.database.models import IssueModel

    # Create organization, project, and sprint
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

    sprint = SprintModel(
        project_id=project.id,
        name="Sprint 1",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 14),
        status="active",
    )
    db_session.add(sprint)
    await db_session.flush()

    # Create issues with story points
    issue1 = IssueModel(
        project_id=project.id,
        title="Issue 1",
        issue_number=1,
        key="TEST-1",
        type="task",
        status="todo",
        priority="medium",
        story_points=5,
    )
    issue2 = IssueModel(
        project_id=project.id,
        title="Issue 2",
        issue_number=2,
        key="TEST-2",
        type="task",
        status="done",
        priority="medium",
        story_points=3,
    )
    db_session.add(issue1)
    db_session.add(issue2)
    await db_session.flush()

    # Add issues to sprint
    from src.infrastructure.database.models import SprintIssueModel

    sprint_issue1 = SprintIssueModel(sprint_id=sprint.id, issue_id=issue1.id, order=0)
    sprint_issue2 = SprintIssueModel(sprint_id=sprint.id, issue_id=issue2.id, order=1)
    db_session.add(sprint_issue1)
    db_session.add(sprint_issue2)
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

    # Get metrics
    metrics_response = await client.get(
        f"/api/v1/sprints/{sprint.id}/metrics",
        headers=auth_headers,
    )

    assert metrics_response.status_code == 200
    data = metrics_response.json()
    assert "total_story_points" in data
    assert "completed_story_points" in data
    assert "remaining_story_points" in data
    assert "completion_percentage" in data
    assert "velocity" in data
    assert "issue_counts" in data
    assert "burndown_data" in data


@pytest.mark.asyncio
async def test_complete_sprint_success(client: AsyncClient, test_user, db_session):
    """Test successful sprint completion."""
    from datetime import date

    # Create organization, project, and sprint
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

    sprint = SprintModel(
        project_id=project.id,
        name="Sprint 1",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 14),
        status="active",
    )
    db_session.add(sprint)
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

    # Complete sprint
    complete_response = await client.post(
        f"/api/v1/sprints/{sprint.id}/complete",
        json={"move_incomplete_to_backlog": True},
        headers=auth_headers,
    )

    assert complete_response.status_code == 200
    data = complete_response.json()
    assert data["sprint_id"] == str(sprint.id)
    assert "metrics" in data

    # Verify sprint status is completed
    get_response = await client.get(
        f"/api/v1/sprints/{sprint.id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
    sprint_data = get_response.json()
    assert sprint_data["status"] == "completed"
