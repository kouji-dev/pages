"""Integration tests for label endpoints."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    IssueModel,
    LabelModel,
    OrganizationMemberModel,
    OrganizationModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_create_label_success(client: AsyncClient, test_user, db_session):
    """Test successful label creation."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        f"/api/v1/projects/{project.id}/labels",
        json={"name": "bug", "color": "#ff0000", "description": "Bug fix"},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "bug"
    assert data["color"] == "#ff0000"
    assert data["description"] == "Bug fix"
    assert data["project_id"] == str(project.id)
    assert "id" in data


@pytest.mark.asyncio
async def test_create_label_duplicate_name(client: AsyncClient, test_user, db_session):
    """Test label creation fails with duplicate name in project."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    existing = LabelModel(project_id=project.id, name="bug", color="#ff0000")
    db_session.add(existing)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        f"/api/v1/projects/{project.id}/labels",
        json={"name": "bug", "color": "#00ff00"},
        headers=auth_headers,
    )
    assert create_response.status_code == 409


@pytest.mark.asyncio
async def test_list_project_labels(client: AsyncClient, test_user, db_session):
    """Test listing project labels."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(
        organization_id=org.id, user_id=test_user.id, role="member"
    )
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    label1 = LabelModel(project_id=project.id, name="bug", color="#ff0000")
    label2 = LabelModel(project_id=project.id, name="feature", color="#00ff00")
    db_session.add_all([label1, label2])
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    list_response = await client.get(
        f"/api/v1/projects/{project.id}/labels",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 2
    assert len(data["labels"]) == 2
    names = {lab["name"] for lab in data["labels"]}
    assert names == {"bug", "feature"}


@pytest.mark.asyncio
async def test_get_label_by_id(client: AsyncClient, test_user, db_session):
    """Test get label by ID."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(
        organization_id=org.id, user_id=test_user.id, role="member"
    )
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    label = LabelModel(project_id=project.id, name="bug", color="#ff0000")
    db_session.add(label)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    get_response = await client.get(
        f"/api/v1/labels/{label.id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(label.id)
    assert data["name"] == "bug"


@pytest.mark.asyncio
async def test_update_label(client: AsyncClient, test_user, db_session):
    """Test update label."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    label = LabelModel(project_id=project.id, name="bug", color="#ff0000")
    db_session.add(label)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    update_response = await client.put(
        f"/api/v1/labels/{label.id}",
        json={"name": "feature", "color": "#00ff00"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "feature"
    assert data["color"] == "#00ff00"


@pytest.mark.asyncio
async def test_add_and_remove_label_on_issue(client: AsyncClient, test_user, db_session):
    """Test add label to issue and remove label from issue."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    issue = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Fix bug",
        type="bug",
        status="todo",
        priority="medium",
    )
    db_session.add(issue)
    await db_session.flush()
    label = LabelModel(project_id=project.id, name="bug", color="#ff0000")
    db_session.add(label)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # List labels on issue (empty)
    list_resp = await client.get(
        f"/api/v1/issues/{issue.id}/labels",
        headers=auth_headers,
    )
    assert list_resp.status_code == 200
    assert list_resp.json() == []

    # Add label to issue
    add_resp = await client.post(
        f"/api/v1/issues/{issue.id}/labels",
        json={"label_id": str(label.id)},
        headers=auth_headers,
    )
    assert add_resp.status_code == 204

    # List labels on issue (one label)
    list_resp2 = await client.get(
        f"/api/v1/issues/{issue.id}/labels",
        headers=auth_headers,
    )
    assert list_resp2.status_code == 200
    assert len(list_resp2.json()) == 1
    assert list_resp2.json()[0]["name"] == "bug"

    # Remove label from issue
    remove_resp = await client.delete(
        f"/api/v1/issues/{issue.id}/labels/{label.id}",
        headers=auth_headers,
    )
    assert remove_resp.status_code == 204

    # List labels on issue (empty again)
    list_resp3 = await client.get(
        f"/api/v1/issues/{issue.id}/labels",
        headers=auth_headers,
    )
    assert list_resp3.status_code == 200
    assert list_resp3.json() == []


@pytest.mark.asyncio
async def test_delete_label(client: AsyncClient, test_user, db_session):
    """Test delete label."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    label = LabelModel(project_id=project.id, name="bug", color="#ff0000")
    db_session.add(label)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    delete_response = await client.delete(
        f"/api/v1/labels/{label.id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/v1/labels/{label.id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404
