"""Integration tests for board endpoints."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    BoardListModel,
    BoardModel,
    OrganizationMemberModel,
    OrganizationModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_create_board_success(client: AsyncClient, test_user, db_session):
    """Test successful board creation (first board is default)."""
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
        f"/api/v1/projects/{project.id}/boards",
        json={"name": "Backlog", "description": "Backlog board"},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "Backlog"
    assert data["description"] == "Backlog board"
    assert data["project_id"] == str(project.id)
    assert data["is_default"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_list_project_boards(client: AsyncClient, test_user, db_session):
    """Test listing project boards."""
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
    board1 = BoardModel(project_id=project.id, name="Backlog", position=0, is_default=True)
    board2 = BoardModel(project_id=project.id, name="Sprint", position=1, is_default=False)
    db_session.add_all([board1, board2])
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    list_response = await client.get(
        f"/api/v1/projects/{project.id}/boards",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 2
    assert len(data["boards"]) == 2
    names = {b["name"] for b in data["boards"]}
    assert names == {"Backlog", "Sprint"}
    assert data["page"] == 1
    assert data["limit"] == 20


@pytest.mark.asyncio
async def test_get_board_by_id_with_lists(client: AsyncClient, test_user, db_session):
    """Test get board by ID including lists."""
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
    board = BoardModel(
        project_id=project.id,
        name="Backlog",
        description="Backlog",
        position=0,
        is_default=True,
    )
    db_session.add(board)
    await db_session.flush()
    list1 = BoardListModel(
        board_id=board.id, list_type="label", list_config={"label_id": None}, position=0
    )
    db_session.add(list1)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    get_response = await client.get(
        f"/api/v1/boards/{board.id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(board.id)
    assert data["name"] == "Backlog"
    assert data["description"] == "Backlog"
    assert "lists" in data
    assert len(data["lists"]) == 1
    assert data["lists"][0]["list_type"] == "label"


@pytest.mark.asyncio
async def test_update_board(client: AsyncClient, test_user, db_session):
    """Test update board."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    board = BoardModel(project_id=project.id, name="Backlog", position=0, is_default=True)
    db_session.add(board)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    update_response = await client.put(
        f"/api/v1/boards/{board.id}",
        json={"name": "Sprint Board", "description": "Active sprint", "position": 1},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Sprint Board"
    assert data["description"] == "Active sprint"
    assert data["position"] == 1


@pytest.mark.asyncio
async def test_delete_board_success(client: AsyncClient, test_user, db_session):
    """Test delete board when project has more than one board."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    board1 = BoardModel(project_id=project.id, name="Backlog", position=0, is_default=True)
    board2 = BoardModel(project_id=project.id, name="Sprint", position=1, is_default=False)
    db_session.add_all([board1, board2])
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    delete_response = await client.delete(
        f"/api/v1/boards/{board2.id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/v1/boards/{board2.id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_last_board_returns_409(client: AsyncClient, test_user, db_session):
    """Test cannot delete last board of project."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    board = BoardModel(project_id=project.id, name="Backlog", position=0, is_default=True)
    db_session.add(board)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    delete_response = await client.delete(
        f"/api/v1/boards/{board.id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 409
