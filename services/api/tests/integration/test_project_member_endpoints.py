"""Integration tests for project member endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    ProjectMemberModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_add_project_member_success(client: AsyncClient, test_user, db_session):
    """Test successful project member addition."""
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

    # Create another user to add
    from src.domain.entities import User
    from src.domain.value_objects import Email, HashedPassword

    another_user = User(
        id=uuid4(),
        email=Email("another@example.com"),
        password_hash=HashedPassword("$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"),
        name="Another User",
    )
    from src.infrastructure.database.models import UserModel

    another_user_model = UserModel(
        id=another_user.id,
        email=another_user.email.value,
        password_hash=another_user.password_hash.value,
        name=another_user.name,
    )
    db_session.add(another_user_model)
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

    # Add member
    add_response = await client.post(
        f"/api/v1/projects/{project.id}/members",
        json={"user_id": str(another_user.id), "role": "member"},
        headers=auth_headers,
    )

    assert add_response.status_code == 201
    data = add_response.json()
    assert data["user_id"] == str(another_user.id)
    assert data["project_id"] == str(project.id)
    assert data["role"] == "member"
    assert data["user_name"] == "Another User"
    assert data["user_email"] == "another@example.com"


@pytest.mark.asyncio
async def test_add_project_member_requires_admin(client: AsyncClient, test_user, db_session):
    """Test add project member requires organization admin."""
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

    # Try to add member
    add_response = await client.post(
        f"/api/v1/projects/{project.id}/members",
        json={"user_id": str(uuid4()), "role": "member"},
        headers=auth_headers,
    )

    assert add_response.status_code == 403


@pytest.mark.asyncio
async def test_add_project_member_already_member(client: AsyncClient, test_user, db_session):
    """Test add project member fails when user is already a member."""
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

    # Add user as project member
    project_member = ProjectMemberModel(
        project_id=project.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(project_member)
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

    # Try to add same member again
    add_response = await client.post(
        f"/api/v1/projects/{project.id}/members",
        json={"user_id": str(test_user.id), "role": "member"},
        headers=auth_headers,
    )

    assert add_response.status_code == 409


@pytest.mark.asyncio
async def test_list_project_members_success(client: AsyncClient, test_user, db_session):
    """Test successful project member listing."""
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

    # Add project members
    project_member1 = ProjectMemberModel(
        project_id=project.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(project_member1)
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

    # List members
    list_response = await client.get(
        f"/api/v1/projects/{project.id}/members",
        headers=auth_headers,
        params={"page": 1, "limit": 20},
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["members"]) == 1
    assert data["total"] == 1
    assert data["page"] == 1
    assert data["limit"] == 20
    assert data["members"][0]["user_id"] == str(test_user.id)
    assert data["members"][0]["role"] == "admin"


@pytest.mark.asyncio
async def test_list_project_members_requires_membership(client: AsyncClient, test_user, db_session):
    """Test list project members requires organization membership."""
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

    # Try to list members
    list_response = await client.get(
        f"/api/v1/projects/{project.id}/members",
        headers=auth_headers,
    )

    assert list_response.status_code == 403


@pytest.mark.asyncio
async def test_update_project_member_role_success(client: AsyncClient, test_user, db_session):
    """Test successful project member role update."""
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

    # Create another user
    from src.domain.entities import User
    from src.domain.value_objects import Email, HashedPassword
    from src.infrastructure.database.models import UserModel

    another_user = User(
        id=uuid4(),
        email=Email("another@example.com"),
        password_hash=HashedPassword("$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"),
        name="Another User",
    )
    another_user_model = UserModel(
        id=another_user.id,
        email=another_user.email.value,
        password_hash=another_user.password_hash.value,
        name=another_user.name,
    )
    db_session.add(another_user_model)
    await db_session.flush()

    # Add another user as project member
    project_member = ProjectMemberModel(
        project_id=project.id,
        user_id=another_user.id,
        role="member",
    )
    db_session.add(project_member)
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

    # Update role
    update_response = await client.put(
        f"/api/v1/projects/{project.id}/members/{another_user.id}",
        json={"role": "admin"},
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["role"] == "admin"
    assert data["user_id"] == str(another_user.id)


@pytest.mark.asyncio
async def test_update_project_member_role_requires_admin(
    client: AsyncClient, test_user, db_session
):
    """Test update project member role requires organization admin."""
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

    # Try to update role
    update_response = await client.put(
        f"/api/v1/projects/{project.id}/members/{test_user.id}",
        json={"role": "admin"},
        headers=auth_headers,
    )

    assert update_response.status_code == 403


@pytest.mark.asyncio
async def test_remove_project_member_success(client: AsyncClient, test_user, db_session):
    """Test successful project member removal."""
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

    # Create another user
    from src.domain.entities import User
    from src.domain.value_objects import Email, HashedPassword
    from src.infrastructure.database.models import UserModel

    another_user = User(
        id=uuid4(),
        email=Email("another@example.com"),
        password_hash=HashedPassword("$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"),
        name="Another User",
    )
    another_user_model = UserModel(
        id=another_user.id,
        email=another_user.email.value,
        password_hash=another_user.password_hash.value,
        name=another_user.name,
    )
    db_session.add(another_user_model)
    await db_session.flush()

    # Add another user as project member
    project_member = ProjectMemberModel(
        project_id=project.id,
        user_id=another_user.id,
        role="member",
    )
    db_session.add(project_member)
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

    # Remove member
    remove_response = await client.delete(
        f"/api/v1/projects/{project.id}/members/{another_user.id}",
        headers=auth_headers,
    )

    assert remove_response.status_code == 204

    # Verify member is removed
    from sqlalchemy import select

    result = await db_session.execute(
        select(ProjectMemberModel).where(
            ProjectMemberModel.project_id == project.id,
            ProjectMemberModel.user_id == another_user.id,
        )
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_remove_project_member_requires_admin(client: AsyncClient, test_user, db_session):
    """Test remove project member requires organization admin."""
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

    # Try to remove member
    remove_response = await client.delete(
        f"/api/v1/projects/{project.id}/members/{test_user.id}",
        headers=auth_headers,
    )

    assert remove_response.status_code == 403

