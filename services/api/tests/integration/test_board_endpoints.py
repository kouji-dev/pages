"""Integration tests for board endpoints."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    BoardListModel,
    BoardModel,
    IssueLabelModel,
    IssueModel,
    LabelModel,
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


# --- Board Lists (Columns) ---


@pytest.mark.asyncio
async def test_create_board_list_success(client: AsyncClient, test_user, db_session):
    """Test POST /boards/:id/lists creates a list (column)."""
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

    create_response = await client.post(
        f"/api/v1/boards/{board.id}/lists",
        json={"list_type": "label", "list_config": {"label_id": None}},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    data = create_response.json()
    assert data["list_type"] == "label"
    assert data["board_id"] == str(board.id)
    assert "id" in data
    assert data["position"] >= 0


@pytest.mark.asyncio
async def test_list_board_lists(client: AsyncClient, test_user, db_session):
    """Test GET /boards/:id/lists returns lists ordered by position."""
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
    board = BoardModel(project_id=project.id, name="Backlog", position=0, is_default=True)
    db_session.add(board)
    await db_session.flush()
    list1 = BoardListModel(
        board_id=board.id, list_type="label", list_config={"label_id": None}, position=0
    )
    list2 = BoardListModel(
        board_id=board.id, list_type="assignee", list_config={"user_id": None}, position=1
    )
    db_session.add_all([list1, list2])
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    list_response = await client.get(
        f"/api/v1/boards/{board.id}/lists",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 2
    assert len(data["lists"]) == 2
    assert data["lists"][0]["position"] == 0
    assert data["lists"][1]["position"] == 1


@pytest.mark.asyncio
async def test_update_board_list(client: AsyncClient, test_user, db_session):
    """Test PUT /board-lists/:id updates position and list_config."""
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
    board_list = BoardListModel(board_id=board.id, list_type="label", list_config={}, position=0)
    db_session.add(board_list)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    update_response = await client.put(
        f"/api/v1/board-lists/{board_list.id}",
        json={"position": 2, "list_config": {"label_id": "00000000-0000-0000-0000-000000000001"}},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["position"] == 2
    assert data["list_config"] == {"label_id": "00000000-0000-0000-0000-000000000001"}


@pytest.mark.asyncio
async def test_delete_board_list(client: AsyncClient, test_user, db_session):
    """Test DELETE /board-lists/:id removes the list."""
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
    board_list = BoardListModel(board_id=board.id, list_type="label", list_config={}, position=0)
    db_session.add(board_list)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    delete_response = await client.delete(
        f"/api/v1/board-lists/{board_list.id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    list_response = await client.get(
        f"/api/v1/boards/{board.id}/lists",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 0


@pytest.mark.asyncio
async def test_get_board_issues(client: AsyncClient, test_user, db_session):
    """Test GET /boards/:id/issues returns lists with issues (scope applied)."""
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
        position=0,
        is_default=True,
        scope_config={"label_ids": []},
    )
    db_session.add(board)
    await db_session.flush()
    board_list = BoardListModel(board_id=board.id, list_type="label", list_config={}, position=0)
    db_session.add(board_list)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    issues_response = await client.get(
        f"/api/v1/boards/{board.id}/issues",
        headers=auth_headers,
    )
    assert issues_response.status_code == 200
    data = issues_response.json()
    assert "lists" in data
    assert len(data["lists"]) == 1
    assert data["lists"][0]["issues"] == []


@pytest.mark.asyncio
async def test_move_board_issue(client: AsyncClient, test_user, db_session):
    """Test PUT /boards/:id/issues/:issue_id/move (drag & drop with label swapping)."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    board = BoardModel(project_id=project.id, name="Kanban", position=0, is_default=True)
    db_session.add(board)
    await db_session.flush()
    label1 = LabelModel(project_id=project.id, name="To Do", color="#aaa")
    label2 = LabelModel(project_id=project.id, name="In Progress", color="#bbb")
    db_session.add_all([label1, label2])
    await db_session.flush()
    list1 = BoardListModel(
        board_id=board.id,
        list_type="label",
        list_config={"label_id": str(label1.id)},
        position=0,
    )
    list2 = BoardListModel(
        board_id=board.id,
        list_type="label",
        list_config={"label_id": str(label2.id)},
        position=1,
    )
    db_session.add_all([list1, list2])
    await db_session.flush()
    issue = IssueModel(
        project_id=project.id,
        title="Move me",
        issue_number=1,
        type="task",
        status="todo",
        priority="medium",
    )
    db_session.add(issue)
    await db_session.flush()
    issue_label = IssueLabelModel(issue_id=issue.id, label_id=label1.id)
    db_session.add(issue_label)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    move_response = await client.put(
        f"/api/v1/boards/{board.id}/issues/{issue.id}/move",
        json={"source_list_id": str(list1.id), "target_list_id": str(list2.id)},
        headers=auth_headers,
    )
    assert move_response.status_code == 200
    data = move_response.json()
    assert data["id"] == str(issue.id)
    assert data["title"] == "Move me"
    assert str(label2.id) in [str(lid) for lid in data["label_ids"]]
    assert str(label1.id) not in [str(lid) for lid in data["label_ids"]]


@pytest.mark.asyncio
async def test_list_project_boards_with_search(client: AsyncClient, test_user, db_session):
    """Test listing project boards with search by name."""
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
    board2 = BoardModel(project_id=project.id, name="Sprint Board", position=1, is_default=False)
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
        params={"search": "Sprint"},
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 1
    assert len(data["boards"]) == 1
    assert data["boards"][0]["name"] == "Sprint Board"


@pytest.mark.asyncio
async def test_set_default_board(client: AsyncClient, test_user, db_session):
    """Test setting a board as default."""
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

    set_default_response = await client.put(
        f"/api/v1/boards/{board2.id}/set-default",
        headers=auth_headers,
    )
    assert set_default_response.status_code == 200
    data = set_default_response.json()
    assert data["id"] == str(board2.id)
    assert data["is_default"] is True

    list_response = await client.get(
        f"/api/v1/projects/{project.id}/boards",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    boards_data = list_response.json()["boards"]
    default_boards = [b for b in boards_data if b["is_default"]]
    assert len(default_boards) == 1
    assert default_boards[0]["id"] == str(board2.id)


@pytest.mark.asyncio
async def test_duplicate_board(client: AsyncClient, test_user, db_session):
    """Test duplicating a board (config and lists)."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    board = BoardModel(
        project_id=project.id,
        name="Backlog",
        description="Main backlog",
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

    dup_response = await client.post(
        f"/api/v1/boards/{board.id}/duplicate",
        headers=auth_headers,
    )
    assert dup_response.status_code == 201
    data = dup_response.json()
    assert data["name"] == "Copy of Backlog"
    assert data["description"] == "Main backlog"
    assert data["project_id"] == str(project.id)
    assert data["is_default"] is False
    assert data["id"] != str(board.id)
    assert len(data["lists"]) == 1
    assert data["lists"][0]["list_type"] == "label"


@pytest.mark.asyncio
async def test_reorder_project_boards(client: AsyncClient, test_user, db_session):
    """Test reordering boards in a project."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    board1 = BoardModel(project_id=project.id, name="First", position=0, is_default=True)
    board2 = BoardModel(project_id=project.id, name="Second", position=1, is_default=False)
    db_session.add_all([board1, board2])
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    reorder_response = await client.put(
        f"/api/v1/projects/{project.id}/boards/reorder",
        json={"board_ids": [str(board2.id), str(board1.id)]},
        headers=auth_headers,
    )
    assert reorder_response.status_code == 204

    list_response = await client.get(
        f"/api/v1/projects/{project.id}/boards",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    boards_data = list_response.json()["boards"]
    assert len(boards_data) == 2
    assert boards_data[0]["name"] == "Second"
    assert boards_data[0]["position"] == 0
    assert boards_data[1]["name"] == "First"
    assert boards_data[1]["position"] == 1


@pytest.mark.asyncio
async def test_update_board_scope(client: AsyncClient, test_user, db_session):
    """Test updating board scope configuration via /boards/:id/scope."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    board = BoardModel(project_id=project.id, name="Scoped Board", position=0, is_default=True)
    db_session.add(board)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    update_scope_response = await client.put(
        f"/api/v1/boards/{board.id}/scope",
        json={
            "label_ids": [],
            "types": ["task", "bug"],
            "priorities": ["medium", "high"],
        },
        headers=auth_headers,
    )
    assert update_scope_response.status_code == 200
    data = update_scope_response.json()
    assert data["id"] == str(board.id)
    assert set(data["scope_config"]["types"]) == {"task", "bug"}
    assert set(data["scope_config"]["priorities"]) == {"medium", "high"}


@pytest.mark.asyncio
async def test_update_board_swimlanes(client: AsyncClient, test_user, db_session):
    """Test PUT /boards/:id/swimlanes updates swimlane_type."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    board = BoardModel(project_id=project.id, name="Board", position=0, is_default=True)
    db_session.add(board)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    put_epic = await client.put(
        f"/api/v1/boards/{board.id}/swimlanes",
        json={"swimlane_type": "epic"},
        headers=auth_headers,
    )
    assert put_epic.status_code == 200
    data = put_epic.json()
    assert data["swimlane_type"] == "epic"

    put_assignee = await client.put(
        f"/api/v1/boards/{board.id}/swimlanes",
        json={"swimlane_type": "assignee"},
        headers=auth_headers,
    )
    assert put_assignee.status_code == 200
    assert put_assignee.json()["swimlane_type"] == "assignee"

    put_none = await client.put(
        f"/api/v1/boards/{board.id}/swimlanes",
        json={"swimlane_type": "none"},
        headers=auth_headers,
    )
    assert put_none.status_code == 200
    assert put_none.json()["swimlane_type"] == "none"


@pytest.mark.asyncio
async def test_get_board_issues_returns_swimlane_type(client: AsyncClient, test_user, db_session):
    """Test GET /boards/:id/issues returns swimlane_type and swimlanes when configured."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()
    board = BoardModel(
        project_id=project.id,
        name="Board",
        position=0,
        is_default=True,
        swimlane_type="epic",
    )
    db_session.add(board)
    await db_session.flush()
    list_model = BoardListModel(board_id=board.id, list_type="label", list_config={}, position=0)
    db_session.add(list_model)
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    issues_response = await client.get(
        f"/api/v1/boards/{board.id}/issues",
        headers=auth_headers,
    )
    assert issues_response.status_code == 200
    data = issues_response.json()
    assert data["swimlane_type"] == "epic"
    assert "swimlanes" in data
    assert isinstance(data["swimlanes"], list)
    assert data["lists"] == []


@pytest.mark.asyncio
async def test_create_group_board_and_set_projects(client: AsyncClient, test_user, db_session):
    """Test creating a group board for an organization and setting its projects."""
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()
    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()
    project1 = ProjectModel(organization_id=org.id, name="Project One", key="P1")
    project2 = ProjectModel(organization_id=org.id, name="Project Two", key="P2")
    db_session.add_all([project1, project2])
    await db_session.flush()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create group board at organization level
    create_resp = await client.post(
        f"/api/v1/organizations/{org.id}/boards",
        json={
            "name": "Group Board",
            "description": "Org-level board",
            "project_ids": [str(project1.id), str(project2.id)],
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    board_data = create_resp.json()
    assert board_data["board_type"] == "group"
    assert board_data["organization_id"] == str(org.id)
    assert board_data["project_id"] == str(project1.id)

    # Replace projects order
    update_resp = await client.post(
        f"/api/v1/boards/{board_data['id']}/projects",
        json={"project_ids": [str(project2.id), str(project1.id)]},
        headers=auth_headers,
    )
    assert update_resp.status_code == 204
