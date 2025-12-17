"""Integration tests for issue link endpoints."""

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
async def test_create_issue_link_success(client: AsyncClient, test_user, db_session):
    """Test successful issue link creation."""
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

    # Create issues
    issue1 = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Source Issue",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    db_session.add(issue1)
    await db_session.flush()

    issue2 = IssueModel(
        project_id=project.id,
        issue_number=2,
        title="Target Issue",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
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

    # Create issue link
    create_response = await client.post(
        f"/api/v1/issues/{issue1.id}/links",
        json={
            "target_issue_id": str(issue2.id),
            "link_type": "blocks",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["source_issue_id"] == str(issue1.id)
    assert data["target_issue_id"] == str(issue2.id)
    assert data["link_type"] == "blocks"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_issue_links_success(client: AsyncClient, test_user, db_session):
    """Test successfully listing issue links."""
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

    # List issue links
    list_response = await client.get(
        f"/api/v1/issues/{issue.id}/links",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert "links" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_create_issue_link_circular_reference(client: AsyncClient, test_user, db_session):
    """Test creating issue link that would create circular reference."""
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

    # Create issues
    issue1 = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Issue 1",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    db_session.add(issue1)
    await db_session.flush()

    issue2 = IssueModel(
        project_id=project.id,
        issue_number=2,
        title="Issue 2",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    db_session.add(issue2)
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

    # Create link issue1 -> issue2
    create_response1 = await client.post(
        f"/api/v1/issues/{issue1.id}/links",
        json={
            "target_issue_id": str(issue2.id),
            "link_type": "blocks",
        },
        headers=auth_headers,
    )
    assert create_response1.status_code == 201

    # Try to create link issue2 -> issue1 (would create circular reference)
    create_response2 = await client.post(
        f"/api/v1/issues/{issue2.id}/links",
        json={
            "target_issue_id": str(issue1.id),
            "link_type": "blocks",
        },
        headers=auth_headers,
    )
    # Should either reject or handle gracefully
    assert create_response2.status_code in [400, 409, 422]


@pytest.mark.asyncio
async def test_create_issue_link_same_issue(client: AsyncClient, test_user, db_session):
    """Test creating issue link with same source and target issue."""
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

    # Try to create link with same source and target
    create_response = await client.post(
        f"/api/v1/issues/{issue.id}/links",
        json={
            "target_issue_id": str(issue.id),
            "link_type": "blocks",
        },
        headers=auth_headers,
    )

    assert create_response.status_code in [400, 422]  # Should reject self-linking
