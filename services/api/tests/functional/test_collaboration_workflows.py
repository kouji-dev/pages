"""Functional tests for collaboration workflows."""

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
async def test_collaboration_presence_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test collaboration presence workflow: Create Page → Get Presence.

    This workflow validates that:
    - Page presence can be retrieved
    - Presence tracking works correctly
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
        slug="test-org-collab",
    )
    space = await create_test_space(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Space",
    )

    # Step 2: Create page
    page = await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Test Page",
        content="Test content",
    )
    page_id = page["id"]

    # Step 3: Get page presence
    presence_response = await client_instance.get(
        f"/api/v1/pages/{page_id}/presence",
        headers=headers,
    )
    assert presence_response.status_code == 200
    presence_data = presence_response.json()
    assert "presences" in presence_data
    assert "total" in presence_data
    assert isinstance(presence_data["presences"], list)
