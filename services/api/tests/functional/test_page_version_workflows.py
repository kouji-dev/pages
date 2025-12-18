"""Functional tests for page version workflows."""

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
async def test_page_version_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test page version workflow: Create Page → Update → List Versions → Restore.

    This workflow validates that:
    - Page versions are automatically created on update
    - Versions can be listed
    - Versions can be restored
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
        slug="test-org-version",
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
        content="Original content",
    )
    page_id = page["id"]

    # Step 3: Update page (should create version automatically)
    update_response = await client_instance.put(
        f"/api/v1/pages/{page_id}",
        json={
            "title": "Updated Page",
            "content": "Updated content",
        },
        headers=headers,
    )
    assert update_response.status_code == 200

    # Step 4: List page versions
    versions_response = await client_instance.get(
        f"/api/v1/pages/{page_id}/versions",
        headers=headers,
    )
    assert versions_response.status_code == 200
    versions_data = versions_response.json()
    assert versions_data["total"] >= 1
    assert len(versions_data["versions"]) >= 1

    # Step 5: Get specific version
    version_id = versions_data["versions"][0]["id"]
    get_version_response = await client_instance.get(
        f"/api/v1/page-versions/{version_id}",
        headers=headers,
    )
    assert get_version_response.status_code == 200
    version_data = get_version_response.json()
    assert version_data["id"] == version_id
    assert "version_number" in version_data

    # Step 6: Restore version
    restore_response = await client_instance.post(
        f"/api/v1/page-versions/{version_id}/restore",
        headers=headers,
    )
    assert restore_response.status_code == 200
    restored_data = restore_response.json()
    assert restored_data["title"] == "Updated Page"
    assert restored_data["content"] == "Updated content"

    # Step 7: Verify new version was created
    versions_response_after = await client_instance.get(
        f"/api/v1/pages/{page_id}/versions",
        headers=headers,
    )
    assert versions_response_after.status_code == 200
    versions_data_after = versions_response_after.json()
    assert versions_data_after["total"] > versions_data["total"]


@pytest.mark.asyncio
async def test_page_version_diff_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test page version diff workflow: Create Page → Update → Get Diff.

    This workflow validates that:
    - Diff can be calculated between versions
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
        slug="test-org-diff",
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
        content="Original content",
    )
    page_id = page["id"]

    # Step 3: Update page
    update_response = await client_instance.put(
        f"/api/v1/pages/{page_id}",
        json={
            "title": "Updated Page",
            "content": "Updated content",
        },
        headers=headers,
    )
    assert update_response.status_code == 200

    # Step 4: List versions
    versions_response = await client_instance.get(
        f"/api/v1/pages/{page_id}/versions",
        headers=headers,
    )
    assert versions_response.status_code == 200
    versions_data = versions_response.json()
    assert versions_data["total"] >= 2

    # Step 5: Get diff between versions
    if len(versions_data["versions"]) >= 2:
        version1_id = versions_data["versions"][1]["id"]  # Older version
        version2_id = versions_data["versions"][0]["id"]  # Newer version

        diff_response = await client_instance.get(
            f"/api/v1/page-versions/{version2_id}/diff?compare_with={version1_id}",
            headers=headers,
        )
        assert diff_response.status_code == 200
        diff_data = diff_response.json()
        assert "title_diff" in diff_data
        assert "content_diff" in diff_data
