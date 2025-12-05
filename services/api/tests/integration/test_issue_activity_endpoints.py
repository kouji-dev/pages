"""Integration tests for issue activity endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.infrastructure.database.models import (
    IssueActivityModel,
    IssueModel,
    OrganizationMemberModel,
    OrganizationModel,
    ProjectModel,
    UserModel,
)


@pytest.mark.asyncio
async def test_list_issue_activities_success(client: AsyncClient, test_user, db_session):
    """Test successful listing of issue activities."""
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

    # Create some activities
    activity1 = IssueActivityModel(
        issue_id=issue.id,
        user_id=test_user.id,
        action="created",
    )
    db_session.add(activity1)
    await db_session.flush()

    activity2 = IssueActivityModel(
        issue_id=issue.id,
        user_id=test_user.id,
        action="updated",
        field_name="status",
        old_value="todo",
        new_value="in_progress",
    )
    db_session.add(activity2)
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

    # List activities
    response = await client.get(
        f"/api/v1/issues/{issue.id}/activities",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["limit"] == 50
    assert data["total_pages"] == 1
    assert len(data["activities"]) == 2

    # Activities should be ordered by created_at DESC (most recent first)
    activities = data["activities"]
    # Find activities by action
    created_activity = next((a for a in activities if a["action"] == "created"), None)
    updated_activity = next((a for a in activities if a["action"] == "updated"), None)

    assert created_activity is not None
    assert created_activity["field_name"] is None
    assert created_activity["user_id"] == str(test_user.id)

    assert updated_activity is not None
    assert updated_activity["field_name"] == "status"
    assert updated_activity["old_value"] == "todo"
    assert updated_activity["new_value"] == "in_progress"
    assert updated_activity["user_id"] == str(test_user.id)
    assert updated_activity["user_name"] == test_user.name
    assert updated_activity["user_email"] == test_user.email.value


@pytest.mark.asyncio
async def test_list_issue_activities_pagination(client: AsyncClient, test_user, db_session):
    """Test pagination for issue activities."""
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
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    db_session.add(issue)
    await db_session.flush()

    # Create 5 activities
    for i in range(5):
        activity = IssueActivityModel(
            issue_id=issue.id,
            user_id=test_user.id,
            action="updated",
            field_name="title",
            old_value=f"Old {i}",
            new_value=f"New {i}",
        )
        db_session.add(activity)
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

    # List activities page 1
    response = await client.get(
        f"/api/v1/issues/{issue.id}/activities?page=1&limit=2",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["total_pages"] == 3
    assert len(data["activities"]) == 2

    # List activities page 2
    response = await client.get(
        f"/api/v1/issues/{issue.id}/activities?page=2&limit=2",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert data["page"] == 2
    assert data["limit"] == 2
    assert data["total_pages"] == 3
    assert len(data["activities"]) == 2


@pytest.mark.asyncio
async def test_list_issue_activities_issue_not_found(client: AsyncClient, test_user, db_session):
    """Test listing activities for non-existent issue."""
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

    # Try to list activities for non-existent issue
    fake_issue_id = uuid4()
    response = await client.get(
        f"/api/v1/issues/{fake_issue_id}/activities",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_issue_activities_unauthorized(client: AsyncClient, test_user, db_session):
    """Test listing activities without authentication."""
    # Create organization
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

    # Try to list activities without token
    response = await client.get(f"/api/v1/issues/{issue.id}/activities")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_issue_creates_activity_log(client: AsyncClient, test_user, db_session):
    """Test that creating an issue creates an activity log."""
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
            "title": "New Issue",
            "description": "A test issue",
            "type": "bug",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    issue_data = create_response.json()
    issue_id = issue_data["id"]

    # Check that activity log was created
    # Convert string UUID to UUID object
    from uuid import UUID

    issue_uuid = UUID(issue_id)
    result = await db_session.execute(
        select(IssueActivityModel).where(IssueActivityModel.issue_id == issue_uuid)
    )
    activities = result.scalars().all()

    assert len(activities) == 1
    assert activities[0].action == "created"
    assert activities[0].user_id == test_user.id
    assert activities[0].field_name is None


@pytest.mark.asyncio
async def test_update_issue_creates_activity_logs(client: AsyncClient, test_user, db_session):
    """Test that updating an issue creates activity logs for changed fields."""
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

    # Update issue (change status and title)
    update_response = await client.put(
        f"/api/v1/issues/{issue.id}",
        json={
            "status": "in_progress",
            "title": "Updated Title",
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200

    # Check that activity logs were created
    result = await db_session.execute(
        select(IssueActivityModel).where(IssueActivityModel.issue_id == issue.id)
    )
    activities = result.scalars().all()

    # Should have 2 activity logs: one for status change, one for title change
    assert len(activities) >= 2

    # Find status change activity
    status_activity = next(
        (a for a in activities if a.action == "status_changed" and a.field_name == "status"), None
    )
    assert status_activity is not None
    assert status_activity.old_value == "todo"
    assert status_activity.new_value == "in_progress"
    assert status_activity.user_id == test_user.id

    # Find title change activity
    title_activity = next(
        (a for a in activities if a.action == "updated" and a.field_name == "title"), None
    )
    assert title_activity is not None
    assert title_activity.old_value == "Test Issue"
    assert title_activity.new_value == "Updated Title"
    assert title_activity.user_id == test_user.id


@pytest.mark.asyncio
async def test_delete_issue_creates_activity_log(client: AsyncClient, test_user, db_session):
    """Test that deleting an issue creates an activity log."""
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

    # Check that activity log was created
    result = await db_session.execute(
        select(IssueActivityModel).where(IssueActivityModel.issue_id == issue.id)
    )
    activities = result.scalars().all()

    # Should have at least one activity log for deletion
    delete_activities = [a for a in activities if a.action == "deleted"]
    assert len(delete_activities) >= 1
    assert delete_activities[0].user_id == test_user.id
    assert delete_activities[0].field_name is None

