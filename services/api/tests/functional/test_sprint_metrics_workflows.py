"""Functional tests for sprint metrics and completion workflows."""

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
async def test_sprint_metrics_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test sprint metrics: Create Sprint → Add Issues → Get Metrics → Complete.

    This workflow validates that:
    - Sprint metrics can be retrieved
    - Metrics include velocity, completion percentage, issue counts
    - Sprint can be completed with metrics
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
        slug="test-org-sprint-metrics",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )
    project_id = project["id"]

    # Step 2: Create sprint with dates
    sprint_response = await client_instance.post(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
        json={
            "name": "Sprint 1",
            "start_date": "2024-01-01",
            "end_date": "2024-01-14",
            "status": "active",
        },
    )
    assert sprint_response.status_code == 201
    sprint_id = sprint_response.json()["id"]

    # Step 3: Create issues with story points
    issue1 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Issue 1",
        story_points=5,
    )
    issue2 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Issue 2",
        story_points=3,
    )
    issue3 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Issue 3",
        story_points=2,
    )

    # Step 4: Add issues to sprint
    await client_instance.put(
        f"/api/v1/sprints/{sprint_id}/issues",
        headers=headers,
        json={"issue_id": issue1["id"], "order": 0},
    )
    await client_instance.put(
        f"/api/v1/sprints/{sprint_id}/issues",
        headers=headers,
        json={"issue_id": issue2["id"], "order": 1},
    )
    await client_instance.put(
        f"/api/v1/sprints/{sprint_id}/issues",
        headers=headers,
        json={"issue_id": issue3["id"], "order": 2},
    )

    # Step 5: Get metrics (before completion)
    metrics_response = await client_instance.get(
        f"/api/v1/sprints/{sprint_id}/metrics",
        headers=headers,
    )
    assert metrics_response.status_code == 200
    metrics = metrics_response.json()
    assert metrics["total_story_points"] == 10  # 5 + 3 + 2
    assert metrics["completed_story_points"] == 0
    assert metrics["remaining_story_points"] == 10
    assert metrics["completion_percentage"] == 0.0
    assert metrics["velocity"] == 0.0
    assert "issue_counts" in metrics
    assert "burndown_data" in metrics

    # Step 6: Complete sprint
    complete_response = await client_instance.post(
        f"/api/v1/sprints/{sprint_id}/complete",
        headers=headers,
        json={"move_incomplete_to_backlog": True},
    )
    assert complete_response.status_code == 200
    complete_data = complete_response.json()
    assert complete_data["sprint_id"] == sprint_id
    assert "metrics" in complete_data
    assert "total_story_points" in complete_data["metrics"]

    # Step 7: Verify sprint status is completed
    get_sprint_response = await client_instance.get(
        f"/api/v1/sprints/{sprint_id}",
        headers=headers,
    )
    assert get_sprint_response.status_code == 200
    sprint_data = get_sprint_response.json()
    assert sprint_data["status"] == "completed"


@pytest.mark.asyncio
async def test_sprint_completion_with_incomplete_issues(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test sprint completion moves incomplete issues to backlog."""
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
        slug="test-org-sprint-complete",
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
        json={"name": "Sprint 1", "status": "active"},
    )
    assert sprint_response.status_code == 201
    sprint_id = sprint_response.json()["id"]

    # Step 3: Create and add issues
    issue1 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Done Issue",
        status="done",
    )
    issue2 = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Incomplete Issue",
        status="todo",
    )

    await client_instance.put(
        f"/api/v1/sprints/{sprint_id}/issues",
        headers=headers,
        json={"issue_id": issue1["id"], "order": 0},
    )
    await client_instance.put(
        f"/api/v1/sprints/{sprint_id}/issues",
        headers=headers,
        json={"issue_id": issue2["id"], "order": 1},
    )

    # Step 4: Complete sprint
    complete_response = await client_instance.post(
        f"/api/v1/sprints/{sprint_id}/complete",
        headers=headers,
        json={"move_incomplete_to_backlog": True},
    )
    assert complete_response.status_code == 200
    complete_data = complete_response.json()
    assert complete_data["incomplete_issues_moved"] == 1

    # Step 5: Verify incomplete issue is in backlog
    backlog_response = await client_instance.get(
        f"/api/v1/projects/{project_id}/backlog",
        headers=headers,
    )
    assert backlog_response.status_code == 200
    backlog_data = backlog_response.json()
    assert issue2["id"] in backlog_data["issues"]
    assert issue1["id"] not in backlog_data["issues"]  # Done issue should not be in backlog
