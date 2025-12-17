"""Functional tests for issue linking workflow."""

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
async def test_issue_linking_workflow(client: AsyncClient, test_user, db_session):
    """Test complete issue linking workflow."""
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

    # 1. Create issue link
    create_response = await client.post(
        f"/api/v1/issues/{issue1.id}/links",
        json={
            "target_issue_id": str(issue2.id),
            "link_type": "blocks",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    link_data = create_response.json()
    link_id = link_data["id"]

    # 2. List issue links
    list_response = await client.get(
        f"/api/v1/issues/{issue1.id}/links",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 1

    # 3. Delete issue link
    delete_response = await client.delete(
        f"/api/v1/issue-links/{link_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204
