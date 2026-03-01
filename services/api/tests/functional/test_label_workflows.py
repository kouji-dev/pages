"""Functional tests for label workflows."""

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
async def test_label_crud_and_issue_labels_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test full label workflow: create project → create labels → create issue → add/remove labels.

    - Create org, project, two labels
    - Create issue, add labels to issue, list labels, remove label
    - Get/update/delete label
    """
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
        name="Label Test Org",
        slug="label-test-org",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Label Project",
        key="LBL",
    )
    project_id = project["id"]

    # Create two labels
    label1_resp = await client_instance.post(
        f"/api/v1/projects/{project_id}/labels",
        json={"name": "bug", "color": "#ff0000", "description": "Bug fix"},
        headers=headers,
    )
    assert label1_resp.status_code == 201
    label1 = label1_resp.json()
    assert label1["name"] == "bug"
    assert label1["color"] == "#ff0000"

    label2_resp = await client_instance.post(
        f"/api/v1/projects/{project_id}/labels",
        json={"name": "feature", "color": "#00ff00"},
        headers=headers,
    )
    assert label2_resp.status_code == 201
    label2 = label2_resp.json()

    # List project labels
    list_labels_resp = await client_instance.get(
        f"/api/v1/projects/{project_id}/labels",
        headers=headers,
    )
    assert list_labels_resp.status_code == 200
    list_data = list_labels_resp.json()
    assert list_data["total"] == 2
    assert len(list_data["labels"]) == 2

    # Create issue
    issue = await create_test_issue(
        client_instance,
        headers,
        project_id=project_id,
        title="Implement labels",
    )
    issue_id = issue["id"]

    # Issue labels initially empty
    issue_labels_resp = await client_instance.get(
        f"/api/v1/issues/{issue_id}/labels",
        headers=headers,
    )
    assert issue_labels_resp.status_code == 200
    assert issue_labels_resp.json() == []

    # Add label to issue
    add_resp = await client_instance.post(
        f"/api/v1/issues/{issue_id}/labels",
        json={"label_id": label1["id"]},
        headers=headers,
    )
    assert add_resp.status_code == 204

    add_resp2 = await client_instance.post(
        f"/api/v1/issues/{issue_id}/labels",
        json={"label_id": label2["id"]},
        headers=headers,
    )
    assert add_resp2.status_code == 204

    # List issue labels
    issue_labels_resp2 = await client_instance.get(
        f"/api/v1/issues/{issue_id}/labels",
        headers=headers,
    )
    assert issue_labels_resp2.status_code == 200
    labels_on_issue = issue_labels_resp2.json()
    assert len(labels_on_issue) == 2
    names = {lab["name"] for lab in labels_on_issue}
    assert names == {"bug", "feature"}

    # Remove one label
    remove_resp = await client_instance.delete(
        f"/api/v1/issues/{issue_id}/labels/{label2['id']}",
        headers=headers,
    )
    assert remove_resp.status_code == 204

    issue_labels_resp3 = await client_instance.get(
        f"/api/v1/issues/{issue_id}/labels",
        headers=headers,
    )
    assert len(issue_labels_resp3.json()) == 1
    assert issue_labels_resp3.json()[0]["name"] == "bug"

    # Get label by ID
    get_label_resp = await client_instance.get(
        f"/api/v1/labels/{label1['id']}",
        headers=headers,
    )
    assert get_label_resp.status_code == 200
    assert get_label_resp.json()["name"] == "bug"

    # Update label
    update_resp = await client_instance.put(
        f"/api/v1/labels/{label1['id']}",
        json={"name": "bugfix", "color": "#cc0000"},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "bugfix"

    # Delete second label (no longer on issue)
    delete_resp = await client_instance.delete(
        f"/api/v1/labels/{label2['id']}",
        headers=headers,
    )
    assert delete_resp.status_code == 204

    get_deleted = await client_instance.get(
        f"/api/v1/labels/{label2['id']}",
        headers=headers,
    )
    assert get_deleted.status_code == 404
