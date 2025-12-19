"""Functional tests for macro workflows."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    authenticated_client,
    create_test_organization,
    create_test_user,
)


@pytest.mark.asyncio
async def test_macro_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test macro workflow: Create Macro → Execute → Update → List → Delete.

    This workflow validates that:
    - Macros can be created in organizations
    - Macros can be executed
    - Macros can be updated
    - Macros can be listed
    - Macros can be deleted
    """
    # Step 1: Create organization
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    client_instance, headers, _ = await authenticated_client(client, user_data)
    await create_test_organization(
        client_instance,
        headers,
        name="Test Org",
        slug="test-org-macro",
    )

    # Step 2: Create macro
    create_response = await client_instance.post(
        "/api/v1/macros/",
        json={
            "name": "Test Macro",
            "code": "return 'Hello, World!';",
            "macro_type": "code_block",
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    macro = create_response.json()
    macro_id = macro["id"]
    assert macro["name"] == "Test Macro"

    # Step 3: Get macro
    get_response = await client_instance.get(
        f"/api/v1/macros/{macro_id}",
        headers=headers,
    )
    assert get_response.status_code == 200
    macro_data = get_response.json()
    assert macro_data["id"] == macro_id
    assert macro_data["code"] == "return 'Hello, World!';"

    # Step 4: Execute macro
    execute_response = await client_instance.post(
        "/api/v1/macros/execute",
        json={
            "macro_name": "Test Macro",
            "config": {},
        },
        headers=headers,
    )
    assert execute_response.status_code == 200
    execute_data = execute_response.json()
    assert "output" in execute_data

    # Step 5: Update macro
    update_response = await client_instance.put(
        f"/api/v1/macros/{macro_id}",
        json={
            "name": "Updated Macro",
            "code": "return 'Updated!';",
        },
        headers=headers,
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["name"] == "Updated Macro"

    # Step 6: List macros
    list_response = await client_instance.get(
        "/api/v1/macros/",
        headers=headers,
    )
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["total"] >= 1
    assert len(list_data["macros"]) >= 1

    # Step 7: Delete macro
    delete_response = await client_instance.delete(
        f"/api/v1/macros/{macro_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    # Step 8: Verify macro is deleted
    get_deleted_response = await client_instance.get(
        f"/api/v1/macros/{macro_id}",
        headers=headers,
    )
    assert get_deleted_response.status_code == 404
