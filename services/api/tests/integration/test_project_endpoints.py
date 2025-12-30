"""Integration tests for project endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_create_project_success(client: AsyncClient, test_user, db_session):
    """Test successful project creation."""
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

    # Create project
    create_response = await client.post(
        "/api/v1/projects/",
        json={
            "organization_id": str(org.id),
            "name": "My New Project",
            "key": "NEW",
            "description": "A test project",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "My New Project"
    assert data["key"] == "NEW"
    assert data["description"] == "A test project"
    assert data["organization_id"] == str(org.id)
    assert data["member_count"] == 1  # Creator is automatically added as admin
    assert data["issue_count"] == 0
    assert "id" in data


@pytest.mark.asyncio
async def test_create_project_auto_key(client: AsyncClient, test_user, db_session):
    """Test project creation with auto-generated key."""
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

    # Create project without key
    create_response = await client.post(
        "/api/v1/projects/",
        json={
            "organization_id": str(org.id),
            "name": "My Awesome Project",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "My Awesome Project"
    assert data["key"] == "MYAWESOMEP"  # Auto-generated from name (max 10 chars)
    assert data["organization_id"] == str(org.id)


@pytest.mark.asyncio
async def test_create_project_requires_auth(client: AsyncClient):
    """Test project creation requires authentication."""
    response = await client.post(
        "/api/v1/projects/",
        json={
            "organization_id": str(uuid4()),
            "name": "Test Project",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_project_requires_org_membership(client: AsyncClient, test_user, db_session):
    """Test project creation requires organization membership."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Login to get token (user is NOT a member)
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

    # Try to create project
    create_response = await client.post(
        "/api/v1/projects/",
        json={
            "organization_id": str(org.id),
            "name": "Test Project",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 403


@pytest.mark.asyncio
async def test_create_project_key_conflict(client: AsyncClient, test_user, db_session):
    """Test project creation fails with duplicate key in organization."""
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

    # Create existing project
    existing_project = ProjectModel(
        organization_id=org.id,
        name="Existing Project",
        key="TEST",
    )
    db_session.add(existing_project)
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

    # Try to create project with same key
    create_response = await client.post(
        "/api/v1/projects/",
        json={
            "organization_id": str(org.id),
            "name": "New Project",
            "key": "TEST",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 409
    error_data = create_response.json()
    error_message = error_data.get("message", error_data.get("detail", ""))
    assert "key" in error_message.lower() or "already exists" in error_message.lower()


@pytest.mark.asyncio
async def test_get_project_success(client: AsyncClient, test_user, db_session):
    """Test successful project retrieval."""
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

    # Get project
    get_response = await client.get(
        f"/api/v1/projects/{project.id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(project.id)
    assert data["name"] == "Test Project"
    assert data["key"] == "TEST"
    assert data["organization_id"] == str(org.id)


@pytest.mark.asyncio
async def test_get_project_not_found(client: AsyncClient, test_user):
    """Test get project fails when not found."""
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
        f"/api/v1/projects/{fake_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_project_requires_membership(client: AsyncClient, test_user, db_session):
    """Test get project requires organization membership."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Create project (user is NOT a member)
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

    # Try to get project
    get_response = await client.get(
        f"/api/v1/projects/{project.id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 403


@pytest.mark.asyncio
async def test_list_projects_success(client: AsyncClient, test_user, db_session):
    """Test successful project listing."""
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

    # Create projects
    project1 = ProjectModel(
        organization_id=org.id,
        name="Project 1",
        key="PROJ1",
    )
    project2 = ProjectModel(
        organization_id=org.id,
        name="Project 2",
        key="PROJ2",
    )
    db_session.add_all([project1, project2])
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

    # List projects
    list_response = await client.get(
        "/api/v1/projects/",
        headers=auth_headers,
        params={"organization_id": str(org.id), "page": 1, "limit": 20},
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["projects"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["limit"] == 20

    # Check new fields
    for project in data["projects"]:
        assert "deleted_at" in project
        assert project["deleted_at"] is None  # Active projects
        assert "completed_issues_count" in project
        assert project["completed_issues_count"] == 0  # No issues yet
        assert "members" in project
        assert isinstance(project["members"], list)


@pytest.mark.asyncio
async def test_list_projects_with_search(client: AsyncClient, test_user, db_session):
    """Test project listing with search query."""
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

    # Create projects
    project1 = ProjectModel(
        organization_id=org.id,
        name="Frontend Project",
        key="FE",
    )
    project2 = ProjectModel(
        organization_id=org.id,
        name="Backend Project",
        key="BE",
    )
    db_session.add_all([project1, project2])
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

    # Search projects
    list_response = await client.get(
        "/api/v1/projects/",
        headers=auth_headers,
        params={"organization_id": str(org.id), "search": "Frontend"},
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["projects"]) == 1
    assert data["projects"][0]["name"] == "Frontend Project"

    # Check new fields
    project = data["projects"][0]
    assert "deleted_at" in project
    assert "completed_issues_count" in project
    assert "members" in project


@pytest.mark.asyncio
async def test_list_projects_with_members_and_issues(client: AsyncClient, test_user, db_session):
    """Test project listing with members and completed issues."""
    from src.infrastructure.database.models import IssueModel, ProjectMemberModel, UserModel

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

    # Create another user
    other_user = UserModel(
        email="other@example.com",
        password_hash="hash",
        name="Other User",
    )
    db_session.add(other_user)
    await db_session.flush()

    # Create project
    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    # Add members to project
    project_member1 = ProjectMemberModel(
        project_id=project.id,
        user_id=test_user.id,
        role="admin",
    )
    project_member2 = ProjectMemberModel(
        project_id=project.id,
        user_id=other_user.id,
        role="member",
    )
    db_session.add_all([project_member1, project_member2])
    await db_session.flush()

    # Create issues
    issue1 = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Done Issue",
        status="done",
    )
    issue2 = IssueModel(
        project_id=project.id,
        issue_number=2,
        title="Todo Issue",
        status="todo",
    )
    issue3 = IssueModel(
        project_id=project.id,
        issue_number=3,
        title="Another Done Issue",
        status="done",
    )
    db_session.add_all([issue1, issue2, issue3])
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

    # List projects
    list_response = await client.get(
        "/api/v1/projects/",
        headers=auth_headers,
        params={"organization_id": str(org.id), "page": 1, "limit": 20},
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["projects"]) == 1

    project_data = data["projects"][0]
    assert project_data["name"] == "Test Project"
    assert project_data["deleted_at"] is None
    assert project_data["member_count"] == 2
    assert project_data["issue_count"] == 3
    assert project_data["completed_issues_count"] == 2  # 2 issues with status "done"
    assert len(project_data["members"]) == 2  # Top 5, but we have only 2

    # Check members data
    member_user_ids = [m["user_id"] for m in project_data["members"]]
    assert str(test_user.id) in member_user_ids
    assert str(other_user.id) in member_user_ids

    # Check member details
    test_user_member = next(m for m in project_data["members"] if m["user_id"] == str(test_user.id))
    assert test_user_member["user_name"] == test_user.name
    assert test_user_member["role"] == "admin"
    assert test_user_member["project_id"] == str(project.id)


@pytest.mark.asyncio
async def test_list_projects_requires_membership(client: AsyncClient, test_user, db_session):
    """Test list projects requires organization membership."""
    # Create organization (user is NOT a member)
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
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

    # Try to list projects
    list_response = await client.get(
        "/api/v1/projects/",
        headers=auth_headers,
        params={"organization_id": str(org.id)},
    )

    assert list_response.status_code == 403


@pytest.mark.asyncio
async def test_update_project_success(client: AsyncClient, test_user, db_session):
    """Test successful project update."""
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

    # Update project
    update_response = await client.put(
        f"/api/v1/projects/{project.id}",
        json={
            "name": "Updated Project",
            "description": "Updated description",
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Project"
    assert data["description"] == "Updated description"
    assert data["key"] == "TEST"  # Key unchanged


@pytest.mark.asyncio
async def test_update_project_requires_membership(client: AsyncClient, test_user, db_session):
    """Test update project requires organization membership."""
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

    # Try to update project
    update_response = await client.put(
        f"/api/v1/projects/{project.id}",
        json={"name": "Updated Project"},
        headers=auth_headers,
    )

    assert update_response.status_code == 403


@pytest.mark.asyncio
async def test_delete_project_success(client: AsyncClient, test_user, db_session):
    """Test successful project deletion (soft delete)."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as admin
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

    # Delete project
    delete_response = await client.delete(
        f"/api/v1/projects/{project.id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    # Verify project is soft deleted (deleted_at is set)
    await db_session.refresh(project)
    assert project.deleted_at is not None


@pytest.mark.asyncio
async def test_delete_project_requires_admin(client: AsyncClient, test_user, db_session):
    """Test delete project requires organization admin role."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member (not admin)
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

    # Try to delete project
    delete_response = await client.delete(
        f"/api/v1/projects/{project.id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 403
