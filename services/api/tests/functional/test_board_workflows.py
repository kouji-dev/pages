"""Functional tests for board workflows."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    authenticated_client,
    create_test_issue,
    create_test_organization,
    create_test_project,
    create_test_user,
)


@pytest.mark.asyncio
async def test_board_crud_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test full board workflow: create project → create boards → get/list/update → delete one.

    - Create org, project
    - Create first board (becomes default), create second board
    - List project boards, get board by ID (with lists)
    - Update board name/description
    - Delete second board (success), try delete last board (409)
    """
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Board Test User",
    )
    client_instance, headers, _ = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance,
        headers,
        name="Board Test Org",
        slug="board-test-org",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Board Project",
        key="BRD",
    )
    project_id = project["id"]

    # Create first board (default)
    board1_resp = await client_instance.post(
        f"/api/v1/projects/{project_id}/boards",
        json={"name": "Backlog", "description": "Backlog board"},
        headers=headers,
    )
    assert board1_resp.status_code == 201
    board1 = board1_resp.json()
    assert board1["name"] == "Backlog"
    assert board1["is_default"] is True
    assert board1["project_id"] == project_id

    # Create second board
    board2_resp = await client_instance.post(
        f"/api/v1/projects/{project_id}/boards",
        json={"name": "Sprint", "description": "Active sprint", "is_default": False},
        headers=headers,
    )
    assert board2_resp.status_code == 201
    board2 = board2_resp.json()
    assert board2["name"] == "Sprint"
    assert board2["is_default"] is False

    # List project boards
    list_boards_resp = await client_instance.get(
        f"/api/v1/projects/{project_id}/boards",
        headers=headers,
    )
    assert list_boards_resp.status_code == 200
    list_data = list_boards_resp.json()
    assert list_data["total"] == 2
    assert len(list_data["boards"]) == 2
    assert list_data["page"] == 1

    # Get board by ID (with lists)
    get_board_resp = await client_instance.get(
        f"/api/v1/boards/{board1['id']}",
        headers=headers,
    )
    assert get_board_resp.status_code == 200
    get_data = get_board_resp.json()
    assert get_data["id"] == board1["id"]
    assert get_data["name"] == "Backlog"
    assert "lists" in get_data
    assert isinstance(get_data["lists"], list)

    # Update board
    update_resp = await client_instance.put(
        f"/api/v1/boards/{board1['id']}",
        json={"name": "Main Backlog", "description": "Primary backlog"},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Main Backlog"
    assert update_resp.json()["description"] == "Primary backlog"

    # Delete second board (allowed)
    delete2_resp = await client_instance.delete(
        f"/api/v1/boards/{board2['id']}",
        headers=headers,
    )
    assert delete2_resp.status_code == 204

    # Get deleted board returns 404
    get_deleted = await client_instance.get(
        f"/api/v1/boards/{board2['id']}",
        headers=headers,
    )
    assert get_deleted.status_code == 404

    # Try to delete last board (must fail with 409)
    delete_last_resp = await client_instance.delete(
        f"/api/v1/boards/{board1['id']}",
        headers=headers,
    )
    assert delete_last_resp.status_code == 409

    # Board 1 still exists
    get_still = await client_instance.get(
        f"/api/v1/boards/{board1['id']}",
        headers=headers,
    )
    assert get_still.status_code == 200
    assert get_still.json()["name"] == "Main Backlog"


@pytest.mark.asyncio
async def test_board_lists_and_issues_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test board lists (columns) and board issues: create lists → list → update → get issues → delete list."""
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Board Lists User",
    )
    client_instance, headers, _ = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance,
        headers,
        name="Board Lists Org",
        slug="board-lists-org",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Board Lists Project",
        key="BLP",
    )
    project_id = project["id"]

    # Create board
    board_resp = await client_instance.post(
        f"/api/v1/projects/{project_id}/boards",
        json={"name": "Kanban", "description": "Kanban board"},
        headers=headers,
    )
    assert board_resp.status_code == 201
    board = board_resp.json()
    board_id = board["id"]

    # Create first list (column)
    list1_resp = await client_instance.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"list_type": "label", "list_config": {}},
        headers=headers,
    )
    assert list1_resp.status_code == 201
    list1 = list1_resp.json()
    assert list1["list_type"] == "label"
    assert list1["board_id"] == board_id
    list1_id = list1["id"]

    # Create second list
    list2_resp = await client_instance.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"list_type": "assignee", "list_config": {"user_id": None}},
        headers=headers,
    )
    assert list2_resp.status_code == 201
    list2 = list2_resp.json()
    assert list2["list_type"] == "assignee"
    list2_id = list2["id"]

    # List board lists
    lists_resp = await client_instance.get(
        f"/api/v1/boards/{board_id}/lists",
        headers=headers,
    )
    assert lists_resp.status_code == 200
    lists_data = lists_resp.json()
    assert lists_data["total"] == 2
    assert len(lists_data["lists"]) == 2

    # Update first list (position and list_config)
    update_list_resp = await client_instance.put(
        f"/api/v1/board-lists/{list1_id}",
        json={"position": 1, "list_config": {"label_id": None}},
        headers=headers,
    )
    assert update_list_resp.status_code == 200
    assert update_list_resp.json()["position"] == 1

    # Get board issues (grouped by list)
    issues_resp = await client_instance.get(
        f"/api/v1/boards/{board_id}/issues",
        headers=headers,
    )
    assert issues_resp.status_code == 200
    issues_data = issues_resp.json()
    assert "lists" in issues_data
    assert len(issues_data["lists"]) >= 2
    for lst in issues_data["lists"]:
        assert "issues" in lst
        assert "id" in lst
        assert "list_type" in lst

    # Delete second list
    delete_list_resp = await client_instance.delete(
        f"/api/v1/board-lists/{list2_id}",
        headers=headers,
    )
    assert delete_list_resp.status_code == 204

    # List lists again: only one left
    lists_after_resp = await client_instance.get(
        f"/api/v1/boards/{board_id}/lists",
        headers=headers,
    )
    assert lists_after_resp.status_code == 200
    assert lists_after_resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_board_move_issue_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test drag & drop: create board with 2 label lists, create issue with label1, move to list2, verify label swap."""
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Board Move User",
    )
    client_instance, headers, _ = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance,
        headers,
        name="Board Move Org",
        slug="board-move-org",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Board Move Project",
        key="BMP",
    )
    project_id = project["id"]

    # Create two labels
    label1_resp = await client_instance.post(
        f"/api/v1/projects/{project_id}/labels",
        json={"name": "To Do", "color": "#aaa"},
        headers=headers,
    )
    assert label1_resp.status_code == 201
    label1 = label1_resp.json()
    label2_resp = await client_instance.post(
        f"/api/v1/projects/{project_id}/labels",
        json={"name": "Done", "color": "#0f0"},
        headers=headers,
    )
    assert label2_resp.status_code == 201
    label2 = label2_resp.json()

    # Create board
    board_resp = await client_instance.post(
        f"/api/v1/projects/{project_id}/boards",
        json={"name": "Kanban", "description": "Board for move"},
        headers=headers,
    )
    assert board_resp.status_code == 201
    board = board_resp.json()
    board_id = board["id"]

    # Create two lists (label-based) with label_id in list_config
    list1_resp = await client_instance.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"list_type": "label", "list_config": {"label_id": label1["id"]}},
        headers=headers,
    )
    assert list1_resp.status_code == 201
    list1 = list1_resp.json()
    list2_resp = await client_instance.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"list_type": "label", "list_config": {"label_id": label2["id"]}},
        headers=headers,
    )
    assert list2_resp.status_code == 201
    list2 = list2_resp.json()

    # Create issue and add label1
    issue = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Issue to move",
    )
    issue_id = issue["id"]
    add_label_resp = await client_instance.post(
        f"/api/v1/issues/{issue_id}/labels",
        json={"label_id": label1["id"]},
        headers=headers,
    )
    assert add_label_resp.status_code == 204

    # Move issue from list1 to list2 (drag & drop)
    move_resp = await client_instance.put(
        f"/api/v1/boards/{board_id}/issues/{issue_id}/move",
        json={"source_list_id": list1["id"], "target_list_id": list2["id"]},
        headers=headers,
    )
    assert move_resp.status_code == 200
    move_data = move_resp.json()
    assert move_data["id"] == issue_id
    assert move_data["title"] == "Issue to move"
    assert label2["id"] in move_data["label_ids"]
    assert label1["id"] not in move_data["label_ids"]

    # Verify via issue labels endpoint
    issue_labels_resp = await client_instance.get(
        f"/api/v1/issues/{issue_id}/labels",
        headers=headers,
    )
    assert issue_labels_resp.status_code == 200
    labels_on_issue = issue_labels_resp.json()
    label_ids = [lab["id"] for lab in labels_on_issue]
    assert label2["id"] in label_ids
    assert label1["id"] not in label_ids
