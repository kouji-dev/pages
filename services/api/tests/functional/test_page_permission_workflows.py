"""Functional tests for page and space permission workflows."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    authenticated_client,
    create_test_organization,
    create_test_page,
    create_test_space,
    create_test_user,
)


@pytest.mark.asyncio
async def test_page_permission_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test page permission workflow: Create Page → Set Permissions → Get Permissions.

    This workflow validates that:
    - Page permissions can be set for specific users
    - Page permissions can be retrieved
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
        slug="test-org-permission",
    )
    space = await create_test_space(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Space",
    )

    # Step 2: Create another user
    other_user_data = await create_test_user(
        client,
        email=f"other-{unique_email}",
        password=test_password,
        name="Other User",
    )
    other_user_id = other_user_data.get("id") or other_user_data.get("user", {}).get("id")

    # Step 3: Create page
    page = await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Test Page",
        content="Test content",
    )
    page_id = page["id"]

    # Step 4: Set page permissions
    update_response = await client_instance.put(
        f"/api/v1/pages/{page_id}/permissions",
        json={
            "permissions": [
                {
                    "user_id": str(other_user_id),
                    "role": "read",
                }
            ]
        },
        headers=headers,
    )
    assert update_response.status_code == 200
    permissions_data = update_response.json()
    assert len(permissions_data["permissions"]) == 1
    assert permissions_data["permissions"][0]["role"] == "viewer"

    # Step 5: Get page permissions
    get_response = await client_instance.get(
        f"/api/v1/pages/{page_id}/permissions",
        headers=headers,
    )
    assert get_response.status_code == 200
    get_permissions_data = get_response.json()
    assert len(get_permissions_data["permissions"]) == 1
    assert get_permissions_data["permissions"][0]["user_id"] == str(other_user_id)


@pytest.mark.asyncio
async def test_space_permission_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test space permission workflow: Create Space → Set Permissions → Get Permissions.

    This workflow validates that:
    - Space permissions can be set for specific users
    - Space permissions can be retrieved
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
        slug="test-org-space-permission",
    )
    space = await create_test_space(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Space",
    )

    # Step 2: Create another user
    other_user_data = await create_test_user(
        client,
        email=f"other2-{unique_email}",
        password=test_password,
        name="Other User 2",
    )
    other_user_id = other_user_data.get("id") or other_user_data.get("user", {}).get("id")

    # Step 3: Set space permissions
    update_response = await client_instance.put(
        f"/api/v1/spaces/{space['id']}/permissions",
        json={
            "permissions": [
                {
                    "user_id": str(other_user_id),
                    "role": "edit",
                }
            ]
        },
        headers=headers,
    )
    assert update_response.status_code == 200
    permissions_data = update_response.json()
    assert len(permissions_data["permissions"]) == 1
    assert permissions_data["permissions"][0]["role"] == "edit"

    # Step 4: Get space permissions
    get_response = await client_instance.get(
        f"/api/v1/spaces/{space['id']}/permissions",
        headers=headers,
    )
    assert get_response.status_code == 200
    get_permissions_data = get_response.json()
    assert len(get_permissions_data["permissions"]) == 1
    assert get_permissions_data["permissions"][0]["user_id"] == str(other_user_id)
