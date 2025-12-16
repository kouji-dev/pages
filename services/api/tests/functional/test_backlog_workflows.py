"""Functional tests for backlog management workflows."""

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
async def test_backlog_listing_and_filtering_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test backlog listing: Create Issues → List Backlog → Filter → Sort.

    This workflow validates that:
    - Issues not in sprints appear in backlog
    - Backlog can be filtered by type, assignee, priority
    - Backlog can be sorted
    """
    # Step 1: Setup
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
        slug="test-org-backlog",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )
    project_id = project["id"]

    # Step 2: Create issues (not in sprint = in backlog)
    issue1 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Backlog Issue 1",
        issue_type="task",
        priority="high",
    )
    issue2 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Backlog Issue 2",
        issue_type="bug",
        priority="medium",
    )
    issue3 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Backlog Issue 3",
        issue_type="task",
        priority="low",
    )

    # Step 3: List backlog
    backlog_response = await client_instance.get(
        f"/api/v1/projects/{project_id}/backlog",
        headers=headers,
    )
    assert backlog_response.status_code == 200
    backlog_data = backlog_response.json()
    assert backlog_data["total"] == 3
    assert len(backlog_data["issues"]) == 3

    # Step 4: Filter by type
    filtered_response = await client_instance.get(
        f"/api/v1/projects/{project_id}/backlog",
        headers=headers,
        params={"type_filter": "task"},
    )
    assert filtered_response.status_code == 200
    filtered_data = filtered_response.json()
    assert filtered_data["total"] == 2  # Only tasks
    assert issue1["id"] in filtered_data["issues"]
    assert issue3["id"] in filtered_data["issues"]
    assert issue2["id"] not in filtered_data["issues"]

    # Step 5: Filter by priority
    priority_response = await client_instance.get(
        f"/api/v1/projects/{project_id}/backlog",
        headers=headers,
        params={"priority_filter": "high"},
    )
    assert priority_response.status_code == 200
    priority_data = priority_response.json()
    assert priority_data["total"] == 1  # Only high priority
    assert issue1["id"] in priority_data["issues"]


@pytest.mark.asyncio
async def test_backlog_prioritization_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test backlog prioritization: Create Issues → Prioritize → Reorder Single.

    This workflow validates that:
    - Backlog can be prioritized by setting order
    - Single issue can be reordered
    - Order is preserved in backlog listing
    """
    # Step 1: Setup
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
        slug="test-org-backlog-prio",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )
    project_id = project["id"]

    # Step 2: Create issues
    issue1 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Issue 1",
    )
    issue2 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Issue 2",
    )
    issue3 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Issue 3",
    )

    # Step 3: Prioritize backlog (set order)
    prioritize_response = await client_instance.put(
        f"/api/v1/projects/{project_id}/backlog/prioritize",
        headers=headers,
        json={
            "issue_ids": [
                issue3["id"],  # Issue 3 first (highest priority)
                issue1["id"],  # Issue 1 second
                issue2["id"],  # Issue 2 third
            ]
        },
    )
    assert prioritize_response.status_code == 204

    # Step 4: Verify order in backlog listing
    backlog_response = await client_instance.get(
        f"/api/v1/projects/{project_id}/backlog",
        headers=headers,
        params={"sort_by": "backlog_order"},
    )
    assert backlog_response.status_code == 200
    backlog_data = backlog_response.json()
    assert backlog_data["issues"][0] == issue3["id"]  # First in list
    assert backlog_data["issues"][1] == issue1["id"]  # Second
    assert backlog_data["issues"][2] == issue2["id"]  # Third

    # Step 5: Reorder single issue
    reorder_response = await client_instance.put(
        f"/api/v1/projects/{project_id}/backlog/issues/{issue2['id']}/reorder",
        headers=headers,
        json={"position": 0},  # Move to top
    )
    assert reorder_response.status_code == 204

    # Step 6: Verify new order
    backlog_after_reorder = await client_instance.get(
        f"/api/v1/projects/{project_id}/backlog",
        headers=headers,
        params={"sort_by": "backlog_order"},
    )
    assert backlog_after_reorder.status_code == 200
    backlog_after_data = backlog_after_reorder.json()
    assert backlog_after_data["issues"][0] == issue2["id"]  # Now first
