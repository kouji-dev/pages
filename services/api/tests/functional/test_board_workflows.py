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


@pytest.mark.asyncio
async def test_board_management_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test multiple boards management: search, set default, duplicate, reorder.

    - Create project with 3 boards
    - List boards with search by name
    - Set non-default board as default, verify
    - Duplicate a board, verify name and lists
    - Reorder boards, verify new order
    """
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Board Mgmt User",
    )
    client_instance, headers, _ = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance,
        headers,
        name="Board Mgmt Org",
        slug="board-mgmt-org",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Board Mgmt Project",
        key="BMP",
    )
    project_id = project["id"]

    # Create 3 boards
    b1 = (
        await client_instance.post(
            f"/api/v1/projects/{project_id}/boards",
            json={"name": "Backlog", "description": "Backlog"},
            headers=headers,
        )
    ).json()
    b2 = (
        await client_instance.post(
            f"/api/v1/projects/{project_id}/boards",
            json={"name": "Sprint Board", "description": "Sprint"},
            headers=headers,
        )
    ).json()
    b3 = (
        await client_instance.post(
            f"/api/v1/projects/{project_id}/boards",
            json={"name": "Done Board", "description": "Done"},
            headers=headers,
        )
    ).json()
    assert b1["is_default"] is True
    assert b2["is_default"] is False
    assert b3["is_default"] is False

    # List with search
    search_resp = await client_instance.get(
        f"/api/v1/projects/{project_id}/boards",
        params={"search": "Sprint"},
        headers=headers,
    )
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert search_data["total"] == 1
    assert search_data["boards"][0]["name"] == "Sprint Board"

    # Set "Sprint Board" as default
    set_default_resp = await client_instance.put(
        f"/api/v1/boards/{b2['id']}/set-default",
        headers=headers,
    )
    assert set_default_resp.status_code == 200
    assert set_default_resp.json()["is_default"] is True
    list_after = await client_instance.get(
        f"/api/v1/projects/{project_id}/boards",
        headers=headers,
    )
    default_boards = [x for x in list_after.json()["boards"] if x["is_default"]]
    assert len(default_boards) == 1
    assert default_boards[0]["id"] == b2["id"]

    # Duplicate "Backlog" board
    dup_resp = await client_instance.post(
        f"/api/v1/boards/{b1['id']}/duplicate",
        headers=headers,
    )
    assert dup_resp.status_code == 201
    dup_data = dup_resp.json()
    assert dup_data["name"] == "Copy of Backlog"
    assert dup_data["id"] != b1["id"]
    assert dup_data["project_id"] == project_id
    assert dup_data["is_default"] is False

    # Reorder: put Done first, then others
    reorder_resp = await client_instance.put(
        f"/api/v1/projects/{project_id}/boards/reorder",
        json={"board_ids": [b3["id"], b2["id"], b1["id"], dup_data["id"]]},
        headers=headers,
    )
    assert reorder_resp.status_code == 204
    list_after_reorder = await client_instance.get(
        f"/api/v1/projects/{project_id}/boards",
        headers=headers,
    )
    boards_ordered = list_after_reorder.json()["boards"]
    assert len(boards_ordered) == 4
    assert boards_ordered[0]["name"] == "Done Board"
    assert boards_ordered[1]["name"] == "Sprint Board"
    assert boards_ordered[2]["name"] == "Backlog"
    assert boards_ordered[3]["name"] == "Copy of Backlog"


@pytest.mark.asyncio
async def test_board_scope_configuration_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test board scope configuration: set scope and verify filtered issues."""
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Board Scope User",
    )
    client_instance, headers, _ = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance,
        headers,
        name="Board Scope Org",
        slug="board-scope-org",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Board Scope Project",
        key="BSP",
    )
    project_id = project["id"]

    # Create board
    board_resp = await client_instance.post(
        f"/api/v1/projects/{project_id}/boards",
        json={"name": "Scoped", "description": "Scoped board"},
        headers=headers,
    )
    assert board_resp.status_code == 201
    board = board_resp.json()
    board_id = board["id"]

    # Create two labels
    label1_resp = await client_instance.post(
        f"/api/v1/projects/{project_id}/labels",
        json={"name": "Include", "color": "#00ff00"},
        headers=headers,
    )
    assert label1_resp.status_code == 201
    label1 = label1_resp.json()
    label2_resp = await client_instance.post(
        f"/api/v1/projects/{project_id}/labels",
        json={"name": "Exclude", "color": "#ff0000"},
        headers=headers,
    )
    assert label2_resp.status_code == 201
    label2 = label2_resp.json()

    # Create a simple label-based list
    list_resp = await client_instance.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"list_type": "label", "list_config": {}},
        headers=headers,
    )
    assert list_resp.status_code == 201

    # Create two issues and attach different labels
    issue1 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="In scope",
    )
    issue2 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Out of scope",
    )

    # Attach labels
    add_label1_resp = await client_instance.post(
        f"/api/v1/issues/{issue1['id']}/labels",
        json={"label_id": label1["id"]},
        headers=headers,
    )
    assert add_label1_resp.status_code == 204
    add_label2_resp = await client_instance.post(
        f"/api/v1/issues/{issue2['id']}/labels",
        json={"label_id": label2["id"]},
        headers=headers,
    )
    assert add_label2_resp.status_code == 204

    # Update board scope: include label1, exclude label2, type task, priority medium
    scope_resp = await client_instance.put(
        f"/api/v1/boards/{board_id}/scope",
        json={
            "label_ids": [label1["id"]],
            "exclude_label_ids": [label2["id"]],
            "types": ["task"],
            "priorities": ["medium"],
        },
        headers=headers,
    )
    assert scope_resp.status_code == 200

    # Fetch board issues and ensure only first issue is returned
    issues_resp = await client_instance.get(
        f"/api/v1/boards/{board_id}/issues",
        headers=headers,
    )
    assert issues_resp.status_code == 200
    data = issues_resp.json()
    assert len(data["lists"]) == 1
    issues = data["lists"][0]["issues"]
    assert len(issues) == 1
    assert issues[0]["title"] == "In scope"


@pytest.mark.asyncio
async def test_board_swimlanes_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test board swimlanes: set swimlane type and verify GET issues response structure."""
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Board Swimlane User",
    )
    client_instance, headers, _ = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance,
        headers,
        name="Board Swimlane Org",
        slug="board-swimlane-org",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Board Swimlane Project",
        key="BSP",
    )
    project_id = project["id"]

    board_resp = await client_instance.post(
        f"/api/v1/projects/{project_id}/boards",
        json={"name": "Swimlane Board", "description": "Board for swimlanes"},
        headers=headers,
    )
    assert board_resp.status_code == 201
    board = board_resp.json()
    board_id = board["id"]
    assert board.get("swimlane_type") == "none"

    list_resp = await client_instance.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"list_type": "label", "list_config": {}},
        headers=headers,
    )
    assert list_resp.status_code == 201

    put_epic = await client_instance.put(
        f"/api/v1/boards/{board_id}/swimlanes",
        json={"swimlane_type": "epic"},
        headers=headers,
    )
    assert put_epic.status_code == 200
    assert put_epic.json()["swimlane_type"] == "epic"

    issues_resp = await client_instance.get(
        f"/api/v1/boards/{board_id}/issues",
        headers=headers,
    )
    assert issues_resp.status_code == 200
    data = issues_resp.json()
    assert data["swimlane_type"] == "epic"
    assert "swimlanes" in data
    assert isinstance(data["swimlanes"], list)
    assert data["lists"] == []

    put_assignee = await client_instance.put(
        f"/api/v1/boards/{board_id}/swimlanes",
        json={"swimlane_type": "assignee"},
        headers=headers,
    )
    assert put_assignee.status_code == 200
    assert put_assignee.json()["swimlane_type"] == "assignee"

    issues_resp2 = await client_instance.get(
        f"/api/v1/boards/{board_id}/issues",
        headers=headers,
    )
    assert issues_resp2.status_code == 200
    assert issues_resp2.json()["swimlane_type"] == "assignee"
    assert issues_resp2.json()["lists"] == []

    put_none = await client_instance.put(
        f"/api/v1/boards/{board_id}/swimlanes",
        json={"swimlane_type": "none"},
        headers=headers,
    )
    assert put_none.status_code == 200
    assert put_none.json()["swimlane_type"] == "none"

    issues_resp3 = await client_instance.get(
        f"/api/v1/boards/{board_id}/issues",
        headers=headers,
    )
    assert issues_resp3.status_code == 200
    data3 = issues_resp3.json()
    assert data3["swimlane_type"] == "none"
    assert data3["swimlanes"] == []
    assert "lists" in data3
    assert isinstance(data3["lists"], list)


@pytest.mark.asyncio
async def test_group_board_multi_project_aggregation_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test group board over multiple projects aggregates issues from all projects."""
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Group Board User",
    )
    client_instance, headers, _ = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance,
        headers,
        name="Group Org",
        slug="group-org",
    )
    # Create two projects in same org
    project1 = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Project One",
        key="P1",
    )
    project2 = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Project Two",
        key="P2",
    )

    # Create issues in each project
    await create_test_issue(
        client_instance,
        headers,
        project_id=project1["id"],
        title="Issue P1",
    )
    await create_test_issue(
        client_instance,
        headers,
        project_id=project2["id"],
        title="Issue P2",
    )

    # Create group board for organization with both projects
    gb_resp = await client_instance.post(
        f"/api/v1/organizations/{org['id']}/boards",
        json={
            "name": "Group Board",
            "description": "Aggregates P1 and P2",
            "project_ids": [project1["id"], project2["id"]],
        },
        headers=headers,
    )
    assert gb_resp.status_code == 201
    group_board = gb_resp.json()
    board_id = group_board["id"]
    assert group_board["board_type"] == "group"

    # Create a simple list so that GET /boards/:id/lists returns at least one list
    list_resp = await client_instance.post(
        f"/api/v1/boards/{board_id}/lists",
        json={"list_type": "label", "list_config": {}},
        headers=headers,
    )
    assert list_resp.status_code == 201

    # Fetch issues for group board and ensure both issues appear, with project metadata
    issues_resp = await client_instance.get(
        f"/api/v1/boards/{board_id}/issues",
        headers=headers,
    )
    assert issues_resp.status_code == 200
    data = issues_resp.json()
    assert "lists" in data
    # Flatten all issues across lists
    all_issues = []
    for lst in data["lists"]:
        all_issues.extend(lst["issues"])
    titles = {it["title"] for it in all_issues}
    assert {"Issue P1", "Issue P2"}.issubset(titles)
    project_keys = {it["project_key"] for it in all_issues}
    assert "P1" in project_keys
    assert "P2" in project_keys
