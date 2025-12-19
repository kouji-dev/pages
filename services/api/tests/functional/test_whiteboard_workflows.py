"""Functional tests for whiteboard workflows."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    authenticated_client,
    create_test_organization,
    create_test_space,
    create_test_user,
)


@pytest.mark.asyncio
async def test_whiteboard_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test whiteboard workflow: Create Whiteboard → Update → List → Delete.

    This workflow validates that:
    - Whiteboards can be created in spaces
    - Whiteboards can be updated
    - Whiteboards can be listed
    - Whiteboards can be deleted
    """
    # Step 1: Create organization and space
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    client_instance, headers, _ = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance,
        headers,
        name="Test Org",
        slug="test-org-whiteboard",
    )
    space = await create_test_space(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Space",
    )

    # Step 2: Create whiteboard
    create_response = await client_instance.post(
        "/api/v1/whiteboards/",
        json={
            "space_id": space["id"],
            "name": "My Whiteboard",
            "data": {"nodes": [{"id": "1", "type": "text"}], "edges": []},
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    whiteboard = create_response.json()
    whiteboard_id = whiteboard["id"]
    assert whiteboard["name"] == "My Whiteboard"

    # Step 3: Get whiteboard
    get_response = await client_instance.get(
        f"/api/v1/whiteboards/{whiteboard_id}",
        headers=headers,
    )
    assert get_response.status_code == 200
    whiteboard_data = get_response.json()
    assert whiteboard_data["id"] == whiteboard_id
    assert "data" in whiteboard_data

    # Step 4: Update whiteboard
    update_response = await client_instance.put(
        f"/api/v1/whiteboards/{whiteboard_id}",
        json={
            "name": "Updated Whiteboard",
            "data": {"nodes": [{"id": "1"}, {"id": "2"}], "edges": []},
        },
        headers=headers,
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["name"] == "Updated Whiteboard"

    # Step 5: List whiteboards
    list_response = await client_instance.get(
        f"/api/v1/spaces/{space['id']}/whiteboards",
        headers=headers,
    )
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["total"] >= 1
    assert len(list_data["whiteboards"]) >= 1

    # Step 6: Delete whiteboard
    delete_response = await client_instance.delete(
        f"/api/v1/whiteboards/{whiteboard_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    # Step 7: Verify whiteboard is deleted
    get_deleted_response = await client_instance.get(
        f"/api/v1/whiteboards/{whiteboard_id}",
        headers=headers,
    )
    assert get_deleted_response.status_code == 404
