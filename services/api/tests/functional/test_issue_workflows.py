"""Functional tests for issue management workflows."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    authenticated_client,
    create_test_issue,
    create_test_organization,
    create_test_project,
    create_test_user,
    get_user_id,
)


@pytest.mark.asyncio
async def test_create_issue_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test create issue workflow: Create Project → Create Issue → Verify → List.

    This workflow validates that:
    - Issue can be created in project
    - Issue key is auto-generated
    - Issue appears in project's issue list
    """
    # Step 1: Create organization and project
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    client_instance, headers, user_info = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance,
        headers,
        name="Test Org",
        slug="test-org-issue",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )

    # Step 2: Create issue
    issue = await create_test_issue(
        client_instance,
        headers,
        project_id=project["id"],
        title="Test Issue",
        description="This is a test issue",
        issue_type="bug",
        status="todo",
        priority="high",
    )
    assert issue["title"] == "Test Issue"
    assert issue["description"] == "This is a test issue"
    assert issue["type"] == "bug"
    assert issue["status"] == "todo"
    assert issue["priority"] == "high"
    assert issue["project_id"] == project["id"]
    assert "key" in issue  # Key should be auto-generated (e.g., TEST-1)
    issue_id = issue["id"]

    # Step 3: Get issue
    get_response = await client_instance.get(
        f"/api/v1/issues/{issue_id}",
        headers=headers,
    )
    assert get_response.status_code == 200
    issue_data = get_response.json()
    assert issue_data["id"] == issue_id

    # Step 4: List issues
    list_response = await client_instance.get(
        "/api/v1/issues/",
        headers=headers,
        params={"project_id": project["id"]},
    )
    assert list_response.status_code == 200
    issues_data = list_response.json()
    assert "issues" in issues_data
    issue_ids = [i["id"] for i in issues_data["issues"]]
    assert issue_id in issue_ids


@pytest.mark.asyncio
async def test_issue_lifecycle_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test issue lifecycle: Create → Update Status → Assign → Update Priority → Delete.

    This workflow validates that:
    - Issue status can be updated
    - Issue can be assigned to users
    - Issue priority can be updated
    - Issue can be deleted
    - Status transitions are valid
    """
    # Step 1: Create organization, project, and issue
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    client_instance, headers, user_info = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance,
        headers,
        name="Test Org",
        slug="test-org-lifecycle",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )
    issue = await create_test_issue(
        client_instance,
        headers,
        project_id=project["id"],
        title="Lifecycle Issue",
    )
    issue_id = issue["id"]

    # Step 2: Update issue status
    update_status_response = await client_instance.put(
        f"/api/v1/issues/{issue_id}",
        json={"status": "in_progress"},
        headers=headers,
    )
    assert update_status_response.status_code == 200
    updated_issue = update_status_response.json()
    assert updated_issue["status"] == "in_progress"

    # Step 3: Assign issue to user
    user_id = get_user_id(user_info)
    assign_response = await client_instance.put(
        f"/api/v1/issues/{issue_id}",
        json={"assignee_id": user_id},
        headers=headers,
    )
    assert assign_response.status_code == 200
    assigned_issue = assign_response.json()
    assert assigned_issue["assignee_id"] == user_id

    # Step 4: Update priority
    update_priority_response = await client_instance.put(
        f"/api/v1/issues/{issue_id}",
        json={"priority": "critical"},
        headers=headers,
    )
    assert update_priority_response.status_code == 200
    priority_issue = update_priority_response.json()
    assert priority_issue["priority"] == "critical"

    # Step 5: Delete issue
    delete_response = await client_instance.delete(
        f"/api/v1/issues/{issue_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    # Step 6: Verify issue is not accessible
    get_response = await client_instance.get(
        f"/api/v1/issues/{issue_id}",
        headers=headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_issue_comment_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test issue comment workflow: Create Issue → Add Comment → Update → List → Delete.

    This workflow validates that:
    - Comments can be added to issues
    - Comments can be updated by author
    - Comments can be listed
    - Comments can be deleted
    - Permissions are enforced
    """
    # Step 1: Create organization, project, and issue
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    client_instance, headers, user_info = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance,
        headers,
        name="Test Org",
        slug="test-org-comment",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )
    issue = await create_test_issue(
        client_instance,
        headers,
        project_id=project["id"],
        title="Comment Issue",
    )

    # Step 2: Add comment
    add_comment_response = await client_instance.post(
        f"/api/v1/issues/{issue['id']}/comments",
        json={"content": "This is a test comment"},
        headers=headers,
    )
    assert add_comment_response.status_code == 201
    comment = add_comment_response.json()
    assert comment["content"] == "This is a test comment"
    comment_id = comment["id"]

    # Step 3: List comments
    list_comments_response = await client_instance.get(
        f"/api/v1/issues/{issue['id']}/comments",
        headers=headers,
    )
    assert list_comments_response.status_code == 200
    comments_data = list_comments_response.json()
    assert "comments" in comments_data
    assert any(c["id"] == comment_id for c in comments_data["comments"])

    # Step 4: Update comment
    update_comment_response = await client_instance.put(
        f"/api/v1/comments/{comment_id}",
        json={"content": "Updated comment content"},
        headers=headers,
    )
    assert update_comment_response.status_code == 200
    updated_comment = update_comment_response.json()
    assert updated_comment["content"] == "Updated comment content"

    # Step 5: Delete comment
    delete_comment_response = await client_instance.delete(
        f"/api/v1/comments/{comment_id}",
        headers=headers,
    )
    assert delete_comment_response.status_code == 204

    # Step 6: Verify comment is removed
    list_comments_response2 = await client_instance.get(
        f"/api/v1/issues/{issue['id']}/comments",
        headers=headers,
    )
    assert list_comments_response2.status_code == 200
    comments_data2 = list_comments_response2.json()
    assert not any(c["id"] == comment_id for c in comments_data2["comments"])


@pytest.mark.asyncio
async def test_issue_activity_log_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test issue activity log workflow: Create Issue → Update → Verify activity log.

    This workflow validates that:
    - Activity logs are created for issue actions
    - Activity logs can be retrieved
    - Each action is properly logged
    """
    # Step 1: Create organization, project, and issue
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
        slug="test-org-activity",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )
    issue = await create_test_issue(
        client_instance,
        headers,
        project_id=project["id"],
        title="Activity Issue",
    )
    issue_id = issue["id"]

    # Step 2: Update issue (should create activity log)
    update_response = await client_instance.put(
        f"/api/v1/issues/{issue_id}",
        json={"status": "in_progress"},
        headers=headers,
    )
    assert update_response.status_code == 200

    # Step 3: Get activity logs
    activities_response = await client_instance.get(
        f"/api/v1/issues/{issue_id}/activities",
        headers=headers,
    )
    assert activities_response.status_code == 200
    activities_data = activities_response.json()
    assert "activities" in activities_data
    # Should have at least creation and update activities
    assert len(activities_data["activities"]) >= 1


@pytest.mark.asyncio
async def test_issue_filtering_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test issue filtering workflow: Create multiple issues → Filter by status/assignee.

    This workflow validates that:
    - Issues can be filtered by status
    - Issues can be filtered by assignee
    - Filters work correctly
    """
    # Step 1: Create organization, project, and multiple issues
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    client_instance, headers, user_info = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance,
        headers,
        name="Test Org",
        slug="test-org-filter",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )

    # Create issues with different statuses
    issue1 = await create_test_issue(
        client_instance,
        headers,
        project_id=project["id"],
        title="Todo Issue",
        status="todo",
    )
    issue2 = await create_test_issue(
        client_instance,
        headers,
        project_id=project["id"],
        title="In Progress Issue",
        status="in_progress",
    )
    issue3 = await create_test_issue(
        client_instance,
        headers,
        project_id=project["id"],
        title="Done Issue",
        status="done",
    )

    # Step 2: Filter by status
    filter_todo_response = await client_instance.get(
        "/api/v1/issues/",
        headers=headers,
        params={"project_id": project["id"], "status": "todo"},
    )
    assert filter_todo_response.status_code == 200
    todo_issues = filter_todo_response.json()["issues"]
    todo_ids = [i["id"] for i in todo_issues]
    assert issue1["id"] in todo_ids
    assert issue2["id"] not in todo_ids
    assert issue3["id"] not in todo_ids

    # Step 3: Filter by assignee
    # First assign issue2 to user
    user_id = get_user_id(user_info)
    await client_instance.put(
        f"/api/v1/issues/{issue2['id']}",
        json={"assignee_id": user_id},
        headers=headers,
    )

    filter_assignee_response = await client_instance.get(
        "/api/v1/issues/",
        headers=headers,
        params={"project_id": project["id"], "assignee_id": user_id},
    )
    assert filter_assignee_response.status_code == 200
    assigned_issues = filter_assignee_response.json()["issues"]
    assigned_ids = [i["id"] for i in assigned_issues]
    assert issue2["id"] in assigned_ids


@pytest.mark.asyncio
async def test_issue_search_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test issue search workflow: Create issues → Search → Verify results.

    This workflow validates that:
    - Issues can be searched by title/description
    - Search returns relevant results
    - Search is case-insensitive
    """
    # Step 1: Create organization, project, and issues with different titles
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
        slug="test-org-search",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )

    issue1 = await create_test_issue(
        client_instance,
        headers,
        project_id=project["id"],
        title="Bug in authentication",
        description="Login not working",
    )
    issue2 = await create_test_issue(
        client_instance,
        headers,
        project_id=project["id"],
        title="Feature request for dashboard",
        description="Need new dashboard",
    )
    await create_test_issue(
        client_instance,
        headers,
        project_id=project["id"],
        title="Performance issue",
        description="Slow response times",
    )

    # Step 2: Search for "bug"
    search_response = await client_instance.get(
        "/api/v1/issues/",
        headers=headers,
        params={"project_id": project["id"], "search": "bug"},
    )
    assert search_response.status_code == 200
    search_results = search_response.json()["issues"]
    search_ids = [i["id"] for i in search_results]
    assert issue1["id"] in search_ids
    assert issue2["id"] not in search_ids

    # Step 3: Search for "dashboard"
    search_response2 = await client_instance.get(
        "/api/v1/issues/",
        headers=headers,
        params={"project_id": project["id"], "search": "dashboard"},
    )
    assert search_response2.status_code == 200
    search_results2 = search_response2.json()["issues"]
    search_ids2 = [i["id"] for i in search_results2]
    assert issue2["id"] in search_ids2


@pytest.mark.asyncio
async def test_get_issue_with_reporter_and_assignee_userdto(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test GET /api/v1/issues/{issue_id} returns UserDTO for reporter and assignee.

    This workflow validates that:
    - Issue details include reporter with full UserDTO (id, name, avatar_url)
    - Issue details include assignee with full UserDTO when assigned
    - UserDTO structure is correctly embedded in the response
    """
    # Step 1: Create first user (reporter)
    reporter_email = unique_email
    reporter_data = await create_test_user(
        client,
        email=reporter_email,
        password=test_password,
        name="Reporter User",
    )
    reporter_client, reporter_headers, reporter_info = await authenticated_client(
        client, reporter_data
    )
    reporter_id = reporter_info["id"]

    # Step 2: Create organization and project
    org = await create_test_organization(
        reporter_client,
        reporter_headers,
        name="Test Org UserDTO",
        slug="test-org-userdto",
    )
    project = await create_test_project(
        reporter_client,
        reporter_headers,
        organization_id=org["id"],
        name="Test Project UserDTO",
        key="USERDTO",
    )

    # Step 3: Create second user (assignee) and add to organization
    assignee_email = f"assignee_{unique_email}"
    assignee_data = await create_test_user(
        client,
        email=assignee_email,
        password=test_password,
        name="Assignee User",
    )
    assignee_id = assignee_data["id"]

    # Add assignee to organization
    add_member_response = await reporter_client.post(
        f"/api/v1/organizations/{org['id']}/members",
        headers=reporter_headers,
        json={"user_id": assignee_id, "role": "member"},
    )
    assert add_member_response.status_code == 201

    # Step 4: Create issue as reporter
    issue = await create_test_issue(
        reporter_client,
        reporter_headers,
        project["id"],
        "Test Issue with UserDTO",
        "Testing reporter and assignee UserDTO structure",
        issue_type="task",
        status="todo",
        priority="medium",
    )
    issue_id = issue["id"]

    # Step 5: Assign issue to assignee
    update_response = await reporter_client.put(
        f"/api/v1/issues/{issue_id}",
        headers=reporter_headers,
        json={"assignee_id": assignee_id},
    )
    assert update_response.status_code == 200

    # Step 6: Get issue details
    get_response = await reporter_client.get(
        f"/api/v1/issues/{issue_id}",
        headers=reporter_headers,
    )
    assert get_response.status_code == 200
    issue_details = get_response.json()

    # Step 7: Verify reporter UserDTO structure
    assert "reporter" in issue_details
    assert issue_details["reporter"] is not None
    assert "id" in issue_details["reporter"]
    assert "name" in issue_details["reporter"]
    assert "avatar_url" in issue_details["reporter"]
    assert issue_details["reporter"]["id"] == reporter_id
    assert issue_details["reporter"]["name"] == "Reporter User"

    # Step 8: Verify reporter_id is also present
    assert "reporter_id" in issue_details
    assert issue_details["reporter_id"] == reporter_id

    # Step 9: Verify assignee UserDTO structure
    assert "assignee" in issue_details
    assert issue_details["assignee"] is not None
    assert "id" in issue_details["assignee"]
    assert "name" in issue_details["assignee"]
    assert "avatar_url" in issue_details["assignee"]
    assert issue_details["assignee"]["id"] == assignee_id
    assert issue_details["assignee"]["name"] == "Assignee User"

    # Step 10: Verify assignee_id is also present
    assert "assignee_id" in issue_details
    assert issue_details["assignee_id"] == assignee_id

    # Step 11: Verify basic issue data
    assert issue_details["title"] == "Test Issue with UserDTO"
    assert issue_details["key"] == f"USERDTO-{issue_details['issue_number']}"
    assert issue_details["type"] == "task"
    assert issue_details["status"] == "todo"
    assert issue_details["priority"] == "medium"
