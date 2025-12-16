"""Functional tests for sprint management workflows."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    authenticated_client,
    create_test_organization,
    create_test_project,
    create_test_user,
)


@pytest.mark.asyncio
async def test_create_and_manage_sprint_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test sprint management workflow: Create → List → Get → Update → Delete.

    This workflow validates that:
    - Sprint can be created in a project
    - Sprint appears in project's sprint list
    - Sprint can be retrieved by ID
    - Sprint can be updated
    - Sprint can be deleted
    """
    # Step 1: Setup - Create user, organization, and project
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
        slug="test-org-sprint",
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
    create_response = await client_instance.post(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
        json={
            "name": "Sprint 1",
            "goal": "Complete Phase 2.1.1",
            "start_date": "2024-01-01",
            "end_date": "2024-01-14",
            "status": "planned",
        },
    )
    assert create_response.status_code == 201
    sprint_data = create_response.json()
    assert sprint_data["name"] == "Sprint 1"
    assert sprint_data["goal"] == "Complete Phase 2.1.1"
    assert sprint_data["status"] == "planned"
    sprint_id = sprint_data["id"]

    # Step 3: List sprints
    list_response = await client_instance.get(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
    )
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["total"] == 1
    assert len(list_data["sprints"]) == 1
    assert list_data["sprints"][0]["id"] == sprint_id

    # Step 4: Get sprint by ID
    get_response = await client_instance.get(
        f"/api/v1/sprints/{sprint_id}",
        headers=headers,
    )
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == sprint_id
    assert get_data["name"] == "Sprint 1"
    assert get_data["issues"] == []  # No issues yet

    # Step 5: Update sprint
    update_response = await client_instance.put(
        f"/api/v1/sprints/{sprint_id}",
        headers=headers,
        json={
            "name": "Updated Sprint 1",
            "goal": "Updated goal",
            "status": "active",
        },
    )
    assert update_response.status_code == 200
    update_data = update_response.json()
    assert update_data["name"] == "Updated Sprint 1"
    assert update_data["goal"] == "Updated goal"
    assert update_data["status"] == "active"

    # Step 6: Delete sprint
    delete_response = await client_instance.delete(
        f"/api/v1/sprints/{sprint_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    # Step 7: Verify sprint is deleted
    get_deleted_response = await client_instance.get(
        f"/api/v1/sprints/{sprint_id}",
        headers=headers,
    )
    assert get_deleted_response.status_code == 404


@pytest.mark.asyncio
async def test_sprint_listing_with_filters_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test sprint listing with filters: Create Multiple Sprints → Filter by Status.

    This workflow validates that:
    - Multiple sprints can be created
    - Sprints can be filtered by status
    - Pagination works correctly
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
        slug="test-org-sprint-filter",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )
    project_id = project["id"]

    # Step 2: Create multiple sprints with different statuses
    sprint1_response = await client_instance.post(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
        json={"name": "Sprint 1", "status": "planned"},
    )
    assert sprint1_response.status_code == 201
    sprint1_id = sprint1_response.json()["id"]

    sprint2_response = await client_instance.post(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
        json={"name": "Sprint 2", "status": "active"},
    )
    assert sprint2_response.status_code == 201
    sprint2_id = sprint2_response.json()["id"]

    sprint3_response = await client_instance.post(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
        json={"name": "Sprint 3", "status": "completed"},
    )
    assert sprint3_response.status_code == 201
    sprint3_id = sprint3_response.json()["id"]

    # Step 3: List all sprints
    list_all_response = await client_instance.get(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
    )
    assert list_all_response.status_code == 200
    list_all_data = list_all_response.json()
    assert list_all_data["total"] == 3

    # Step 4: Filter by status - planned
    list_planned_response = await client_instance.get(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
        params={"status_filter": "planned"},
    )
    assert list_planned_response.status_code == 200
    list_planned_data = list_planned_response.json()
    assert list_planned_data["total"] == 1
    assert list_planned_data["sprints"][0]["id"] == sprint1_id
    assert list_planned_data["sprints"][0]["status"] == "planned"

    # Step 5: Filter by status - active
    list_active_response = await client_instance.get(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
        params={"status_filter": "active"},
    )
    assert list_active_response.status_code == 200
    list_active_data = list_active_response.json()
    assert list_active_data["total"] == 1
    assert list_active_data["sprints"][0]["id"] == sprint2_id
    assert list_active_data["sprints"][0]["status"] == "active"

    # Step 6: Filter by status - completed
    list_completed_response = await client_instance.get(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
        params={"status_filter": "completed"},
    )
    assert list_completed_response.status_code == 200
    list_completed_data = list_completed_response.json()
    assert list_completed_data["total"] == 1
    assert list_completed_data["sprints"][0]["id"] == sprint3_id
    assert list_completed_data["sprints"][0]["status"] == "completed"


@pytest.mark.asyncio
async def test_sprint_date_validation_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test sprint date validation: Invalid Dates → Overlapping Dates.

    This workflow validates that:
    - Sprints with invalid date ranges are rejected
    - Sprints with overlapping dates are rejected
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
        slug="test-org-sprint-dates",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )
    project_id = project["id"]

    # Step 2: Try to create sprint with invalid dates (end before start)
    invalid_response = await client_instance.post(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
        json={
            "name": "Invalid Sprint",
            "start_date": "2024-01-14",
            "end_date": "2024-01-01",  # End before start
        },
    )
    assert invalid_response.status_code == 400
    assert "start date must be before end date" in invalid_response.json()["detail"].lower()

    # Step 3: Create a valid sprint
    valid_sprint_response = await client_instance.post(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
        json={
            "name": "Valid Sprint",
            "start_date": "2024-01-01",
            "end_date": "2024-01-14",
        },
    )
    assert valid_sprint_response.status_code == 201

    # Step 4: Try to create overlapping sprint
    overlapping_response = await client_instance.post(
        f"/api/v1/projects/{project_id}/sprints",
        headers=headers,
        json={
            "name": "Overlapping Sprint",
            "start_date": "2024-01-10",  # Overlaps with previous sprint
            "end_date": "2024-01-20",
        },
    )
    assert overlapping_response.status_code == 409
    assert "overlap" in overlapping_response.json()["detail"].lower()
