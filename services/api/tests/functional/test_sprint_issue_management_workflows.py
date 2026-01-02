"""Functional tests for sprint issue management workflows."""

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
async def test_sprint_issue_management_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test sprint issue management: Create Sprint → Add Issues → Reorder → Remove.

    This workflow validates that:
    - Issues can be added to a sprint
    - Issues can be reordered within a sprint
    - Issues can be removed from a sprint
    - Issues in active sprints cannot be added to another sprint
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
        slug="test-org-sprint-issues",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )
    project_id = project["id"]

    # Step 2: Create sprint
    sprint_response = await client_instance.post(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
        json={"name": "Sprint 1", "status": "planned"},
    )
    assert sprint_response.status_code == 201
    sprint_id = sprint_response.json()["id"]

    # Step 3: Create issues
    issue1 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Issue 1",
        issue_type="task",
    )
    issue2 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Issue 2",
        issue_type="task",
    )
    issue3 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Issue 3",
        issue_type="task",
    )

    # Step 4: Add issues to sprint
    add_response1 = await client_instance.put(
        f"/api/v1/sprints/{sprint_id}/issues",
        headers=headers,
        json={"issue_id": issue1["id"], "order": 0},
    )
    assert add_response1.status_code == 204

    add_response2 = await client_instance.put(
        f"/api/v1/sprints/{sprint_id}/issues",
        headers=headers,
        json={"issue_id": issue2["id"], "order": 1},
    )
    assert add_response2.status_code == 204

    add_response3 = await client_instance.put(
        f"/api/v1/sprints/{sprint_id}/issues",
        headers=headers,
        json={"issue_id": issue3["id"], "order": 2},
    )
    assert add_response3.status_code == 204

    # Step 5: Verify issues are in sprint
    get_sprint_response = await client_instance.get(
        f"/api/v1/sprints/{sprint_id}",
        headers=headers,
    )
    assert get_sprint_response.status_code == 200
    sprint_data = get_sprint_response.json()
    assert len(sprint_data["issues"]) == 3
    issue_ids = [issue["id"] for issue in sprint_data["issues"]]
    assert issue1["id"] in issue_ids
    assert issue2["id"] in issue_ids
    assert issue3["id"] in issue_ids

    # Step 6: Reorder issues
    reorder_response = await client_instance.put(
        f"/api/v1/sprints/{sprint_id}/issues/reorder",
        headers=headers,
        json={
            "issue_orders": {
                str(issue3["id"]): 0,
                str(issue1["id"]): 1,
                str(issue2["id"]): 2,
            }
        },
    )
    assert reorder_response.status_code == 204

    # Step 7: Remove issue from sprint
    remove_response = await client_instance.delete(
        f"/api/v1/sprints/{sprint_id}/issues/{issue2['id']}",
        headers=headers,
    )
    assert remove_response.status_code == 204

    # Step 8: Verify issue removed
    get_sprint_after_remove = await client_instance.get(
        f"/api/v1/sprints/{sprint_id}",
        headers=headers,
    )
    assert get_sprint_after_remove.status_code == 200
    sprint_data_after = get_sprint_after_remove.json()
    assert len(sprint_data_after["issues"]) == 2
    issue_ids_after = [issue["id"] for issue in sprint_data_after["issues"]]
    assert issue2["id"] not in issue_ids_after


@pytest.mark.asyncio
async def test_add_issue_to_active_sprint_validation(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test that issues in active sprints cannot be added to another sprint."""
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
        slug="test-org-sprint-active",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )
    project_id = project["id"]

    # Step 2: Create active sprint
    active_sprint_response = await client_instance.post(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
        json={"name": "Active Sprint", "status": "active"},
    )
    assert active_sprint_response.status_code == 201
    active_sprint_id = active_sprint_response.json()["id"]

    # Step 3: Create another sprint
    other_sprint_response = await client_instance.post(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
        json={"name": "Other Sprint", "status": "planned"},
    )
    assert other_sprint_response.status_code == 201
    other_sprint_id = other_sprint_response.json()["id"]

    # Step 4: Create issue and add to active sprint
    issue = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Test Issue",
    )

    add_to_active = await client_instance.put(
        f"/api/v1/sprints/{active_sprint_id}/issues",
        headers=headers,
        json={"issue_id": issue["id"], "order": 0},
    )
    assert add_to_active.status_code == 204

    # Step 5: Try to add same issue to another sprint (should fail)
    add_to_other = await client_instance.put(
        f"/api/v1/sprints/{other_sprint_id}/issues",
        headers=headers,
        json={"issue_id": issue["id"], "order": 0},
    )
    assert add_to_other.status_code == 409
    assert "already in active sprint" in add_to_other.json()["detail"].lower()
