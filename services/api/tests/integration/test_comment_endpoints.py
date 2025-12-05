"""Integration tests for comment endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    CommentModel,
    IssueModel,
    OrganizationMemberModel,
    OrganizationModel,
    ProjectModel,
    UserModel,
)


@pytest.mark.asyncio
async def test_create_comment_success(client: AsyncClient, test_user, db_session):
    """Test successful comment creation."""
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

    # Create issue
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

    # Create comment
    create_response = await client.post(
        f"/api/v1/issues/{issue.id}/comments",
        json={"content": "This is a test comment"},
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["content"] == "This is a test comment"
    assert data["issue_id"] == str(issue.id)
    assert data["user_id"] == str(test_user.id)
    assert data["is_edited"] is False
    assert data["user_name"] == test_user.name
    assert data["user_email"] == test_user.email.value
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_comment_success(client: AsyncClient, test_user, db_session):
    """Test successful comment retrieval."""
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

    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
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

    comment = CommentModel(
        entity_type="issue",
        entity_id=issue.id,
        issue_id=issue.id,
        user_id=test_user.id,
        content="Test comment",
    )
    db_session.add(comment)
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

    # Get comment
    get_response = await client.get(
        f"/api/v1/comments/{comment.id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(comment.id)
    assert data["content"] == "Test comment"
    assert data["user_id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_list_comments_success(client: AsyncClient, test_user, db_session):
    """Test successful comment listing."""
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

    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
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

    # Create comments
    comment1 = CommentModel(
        entity_type="issue",
        entity_id=issue.id,
        issue_id=issue.id,
        user_id=test_user.id,
        content="First comment",
    )
    comment2 = CommentModel(
        entity_type="issue",
        entity_id=issue.id,
        issue_id=issue.id,
        user_id=test_user.id,
        content="Second comment",
    )
    db_session.add(comment1)
    db_session.add(comment2)
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

    # List comments
    list_response = await client.get(
        f"/api/v1/issues/{issue.id}/comments",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 2
    assert len(data["comments"]) == 2
    # Comments should be ordered by created_at ASC
    assert data["comments"][0]["content"] == "First comment"
    assert data["comments"][1]["content"] == "Second comment"


@pytest.mark.asyncio
async def test_update_comment_success(client: AsyncClient, test_user, db_session):
    """Test successful comment update."""
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

    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
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

    comment = CommentModel(
        entity_type="issue",
        entity_id=issue.id,
        issue_id=issue.id,
        user_id=test_user.id,
        content="Original comment",
    )
    db_session.add(comment)
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

    # Update comment
    update_response = await client.put(
        f"/api/v1/comments/{comment.id}",
        json={"content": "Updated comment"},
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["content"] == "Updated comment"
    assert data["is_edited"] is True


@pytest.mark.asyncio
async def test_delete_comment_success(client: AsyncClient, test_user, db_session):
    """Test successful comment deletion."""
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

    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
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

    comment = CommentModel(
        entity_type="issue",
        entity_id=issue.id,
        issue_id=issue.id,
        user_id=test_user.id,
        content="Comment to delete",
    )
    db_session.add(comment)
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

    # Delete comment
    delete_response = await client.delete(
        f"/api/v1/comments/{comment.id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    # Verify comment is soft-deleted
    await db_session.refresh(comment)
    assert comment.deleted_at is not None


@pytest.mark.asyncio
async def test_create_comment_issue_not_found(client: AsyncClient, test_user, db_session):
    """Test comment creation with non-existent issue."""
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

    # Try to create comment on non-existent issue
    create_response = await client.post(
        f"/api/v1/issues/{uuid4()}/comments",
        json={"content": "Test comment"},
        headers=auth_headers,
    )

    assert create_response.status_code == 404


@pytest.mark.asyncio
async def test_update_comment_unauthorized(client: AsyncClient, test_user, db_session):
    """Test comment update by non-author."""
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

    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
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

    # Create another user (with same password as test_user)
    from src.domain.value_objects import Email, HashedPassword, Password
    from src.infrastructure.database.repositories import SQLAlchemyUserRepository
    from src.infrastructure.security import BcryptPasswordService

    user_repo = SQLAlchemyUserRepository(db_session)
    password_service = BcryptPasswordService()

    email = Email("other@example.com")
    password = Password("TestPassword123!")
    hashed_password = password_service.hash(password)

    from src.domain.entities import User

    other_user_entity = User.create(
        email=email,
        password_hash=hashed_password,
        name="Other User",
    )

    other_user_created = await user_repo.create(other_user_entity)
    await db_session.flush()

    # Get the UserModel for later use
    from sqlalchemy import select

    result = await db_session.execute(
        select(UserModel).where(UserModel.id == other_user_created.id)
    )
    other_user = result.scalar_one()

    # Add other user as member
    other_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=other_user.id,
        role="member",
    )
    db_session.add(other_member)
    await db_session.flush()

    comment = CommentModel(
        entity_type="issue",
        entity_id=issue.id,
        issue_id=issue.id,
        user_id=test_user.id,  # Comment belongs to test_user
        content="Original comment",
    )
    db_session.add(comment)
    await db_session.flush()

    # Login as other user
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": other_user.email,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Try to update comment (should fail)
    update_response = await client.put(
        f"/api/v1/comments/{comment.id}",
        json={"content": "Updated comment"},
        headers=auth_headers,
    )

    assert update_response.status_code == 400
    error_data = update_response.json()
    assert "Only the comment author" in error_data.get("message", error_data.get("detail", ""))


@pytest.mark.asyncio
async def test_list_comments_pagination(client: AsyncClient, test_user, db_session):
    """Test comment listing with pagination."""
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

    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
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

    # Create 5 comments
    for i in range(5):
        comment = CommentModel(
            entity_type="issue",
            entity_id=issue.id,
            issue_id=issue.id,
            user_id=test_user.id,
            content=f"Comment {i+1}",
        )
        db_session.add(comment)
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

    # List comments with pagination
    list_response = await client.get(
        f"/api/v1/issues/{issue.id}/comments?page=1&limit=2",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 5
    assert len(data["comments"]) == 2
    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["pages"] == 3

