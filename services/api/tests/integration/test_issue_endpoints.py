"""Integration tests for issue endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_create_issue_success(client: AsyncClient, test_user, db_session):
    """Test successful issue creation."""
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

    # Create issue
    create_response = await client.post(
        "/api/v1/issues/",
        json={
            "project_id": str(project.id),
            "title": "My New Issue",
            "description": "A test issue",
            "type": "bug",
            "status": "todo",
            "priority": "high",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["title"] == "My New Issue"
    assert data["description"] == "A test issue"
    assert data["type"] == "bug"
    assert data["status"] == "todo"
    assert data["priority"] == "high"
    assert data["project_id"] == str(project.id)
    assert data["key"] == "TEST-1"  # Auto-generated key
    assert data["issue_number"] == 1
    assert data["reporter_id"] == str(test_user.id)
    assert "id" in data


@pytest.mark.asyncio
async def test_create_issue_auto_defaults(client: AsyncClient, test_user, db_session):
    """Test issue creation with auto-generated defaults."""
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

    # Create issue with minimal data
    create_response = await client.post(
        "/api/v1/issues/",
        json={
            "project_id": str(project.id),
            "title": "Minimal Issue",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["title"] == "Minimal Issue"
    assert data["type"] == "task"  # Default
    assert data["status"] == "todo"  # Default
    assert data["priority"] == "medium"  # Default
    assert data["key"] == "TEST-1"  # Auto-generated key


@pytest.mark.asyncio
async def test_create_issue_requires_auth(client: AsyncClient):
    """Test issue creation requires authentication."""
    response = await client.post(
        "/api/v1/issues/",
        json={
            "project_id": str(uuid4()),
            "title": "Test Issue",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_issue_requires_membership(client: AsyncClient, test_user, db_session):
    """Test issue creation requires organization membership."""
    # Create organization (user is NOT a member)
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Create project
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

    # Try to create issue
    create_response = await client.post(
        "/api/v1/issues/",
        json={
            "project_id": str(project.id),
            "title": "Test Issue",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 403


@pytest.mark.asyncio
async def test_get_issue_success(client: AsyncClient, test_user, db_session):
    """Test successful issue retrieval."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="member",
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

    # Create issue
    from src.infrastructure.database.models import IssueModel

    issue = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Test Issue",
        description="A test issue",
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

    # Get issue
    get_response = await client.get(
        f"/api/v1/issues/{issue.id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(issue.id)
    assert data["title"] == "Test Issue"
    assert data["key"] == "TEST-1"
    assert data["project_id"] == str(project.id)


@pytest.mark.asyncio
async def test_get_issue_not_found(client: AsyncClient, test_user):
    """Test get issue fails when not found."""
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

    fake_id = str(uuid4())
    get_response = await client.get(
        f"/api/v1/issues/{fake_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_list_issues_success(client: AsyncClient, test_user, db_session):
    """Test successful issue listing."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="member",
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

    # Create issues
    from src.infrastructure.database.models import IssueModel

    issue1 = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Issue 1",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    issue2 = IssueModel(
        project_id=project.id,
        issue_number=2,
        title="Issue 2",
        type="bug",
        status="in_progress",
        priority="high",
        reporter_id=test_user.id,
    )
    db_session.add_all([issue1, issue2])
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

    # List issues
    list_response = await client.get(
        "/api/v1/issues/",
        headers=auth_headers,
        params={"project_id": str(project.id), "page": 1, "limit": 20},
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["issues"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["limit"] == 20
    # Issues are ordered by created_at DESC, so most recent first
    issue_keys = [issue["key"] for issue in data["issues"]]
    assert "TEST-1" in issue_keys
    assert "TEST-2" in issue_keys


@pytest.mark.asyncio
async def test_list_issues_with_filters(client: AsyncClient, test_user, db_session):
    """Test issue listing with filters."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="member",
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

    # Create issues
    from src.infrastructure.database.models import IssueModel

    issue1 = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Task Issue",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    issue2 = IssueModel(
        project_id=project.id,
        issue_number=2,
        title="Bug Issue",
        type="bug",
        status="in_progress",
        priority="high",
        reporter_id=test_user.id,
    )
    db_session.add_all([issue1, issue2])
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
    list_response = await client.get(
        "/api/v1/issues/",
        headers=auth_headers,
        params={"project_id": str(project.id), "type": "bug"},
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["issues"]) == 1
    assert data["issues"][0]["type"] == "bug"


@pytest.mark.asyncio
async def test_list_issues_with_search(client: AsyncClient, test_user, db_session):
    """Test issue listing with search query."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="member",
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

    # Create issues
    from src.infrastructure.database.models import IssueModel

    issue1 = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Frontend Bug",
        description="CSS issue",
        type="bug",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    issue2 = IssueModel(
        project_id=project.id,
        issue_number=2,
        title="Backend Task",
        description="API endpoint",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    db_session.add_all([issue1, issue2])
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

    # Search issues
    list_response = await client.get(
        "/api/v1/issues/",
        headers=auth_headers,
        params={"project_id": str(project.id), "search": "Frontend"},
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["issues"]) == 1
    assert data["issues"][0]["title"] == "Frontend Bug"


@pytest.mark.asyncio
async def test_update_issue_success(client: AsyncClient, test_user, db_session):
    """Test successful issue update."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="member",
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

    # Create issue
    from src.infrastructure.database.models import IssueModel

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

    # Update issue
    update_response = await client.put(
        f"/api/v1/issues/{issue.id}",
        json={
            "title": "Updated Issue",
            "description": "Updated description",
            "status": "in_progress",
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated Issue"
    assert data["description"] == "Updated description"
    assert data["status"] == "in_progress"
    assert data["key"] == "TEST-1"  # Key unchanged


@pytest.mark.asyncio
async def test_update_issue_requires_membership(client: AsyncClient, test_user, db_session):
    """Test update issue requires organization membership."""
    # Create organization (user is NOT a member)
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Create project
    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    # Create issue
    from src.infrastructure.database.models import IssueModel

    issue = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Test Issue",
        type="task",
        status="todo",
        priority="medium",
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

    # Try to update issue
    update_response = await client.put(
        f"/api/v1/issues/{issue.id}",
        json={"title": "Updated Issue"},
        headers=auth_headers,
    )

    assert update_response.status_code == 403


@pytest.mark.asyncio
async def test_delete_issue_success(client: AsyncClient, test_user, db_session):
    """Test successful issue deletion (soft delete)."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="member",
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

    # Create issue
    from src.infrastructure.database.models import IssueModel

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

    # Delete issue
    delete_response = await client.delete(
        f"/api/v1/issues/{issue.id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    # Verify issue is soft deleted (deleted_at is set)
    await db_session.refresh(issue)
    assert issue.deleted_at is not None


@pytest.mark.asyncio
async def test_delete_issue_requires_membership(client: AsyncClient, test_user, db_session):
    """Test delete issue requires organization membership."""
    # Create organization (user is NOT a member)
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Create project
    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    # Create issue
    from src.infrastructure.database.models import IssueModel

    issue = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Test Issue",
        type="task",
        status="todo",
        priority="medium",
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

    # Try to delete issue
    delete_response = await client.delete(
        f"/api/v1/issues/{issue.id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 403
