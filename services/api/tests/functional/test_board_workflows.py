"""Functional tests for board workflows."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    authenticated_client,
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
