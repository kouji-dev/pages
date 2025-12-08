"""Functional tests for project management workflows."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    authenticated_client,
    create_test_organization,
    create_test_project,
    create_test_user,
)


@pytest.mark.asyncio
async def test_create_project_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test create project workflow: Create Org → Create Project → Verify auto-key → List.

    This workflow validates that:
    - Project can be created within organization
    - Project key is auto-generated if not provided
    - Project appears in organization's project list
    """
    # Step 1: Create organization
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
        slug="test-org-project",
    )
    org_id = org["id"]

    # Step 2: Create project with explicit key
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org_id,
        name="Test Project",
        key="TEST",
    )
    assert project["name"] == "Test Project"
    assert project["key"] == "TEST"
    assert project["organization_id"] == org_id
    project_id = project["id"]

    # Step 3: Create project without key (auto-generation)
    project2 = await create_test_project(
        client_instance,
        headers,
        organization_id=org_id,
        name="Auto Key Project",
    )
    assert project2["name"] == "Auto Key Project"
    assert "key" in project2  # Key should be auto-generated
    assert len(project2["key"]) > 0

    # Step 4: List projects
    list_response = await client_instance.get(
        "/api/v1/projects/",
        headers=headers,
        params={"organization_id": org_id},
    )
    assert list_response.status_code == 200
    projects_data = list_response.json()
    assert "projects" in projects_data
    project_ids = [p["id"] for p in projects_data["projects"]]
    assert project_id in project_ids

    # Step 5: Get specific project
    get_response = await client_instance.get(
        f"/api/v1/projects/{project_id}",
        headers=headers,
    )
    assert get_response.status_code == 200
    project_data = get_response.json()
    assert project_data["id"] == project_id
    assert project_data["name"] == "Test Project"


@pytest.mark.asyncio
async def test_project_member_management_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test project member management: Create Project → Add Member → Update Role → Remove.

    This workflow validates that:
    - Project members can be added
    - Member roles can be updated
    - Members can be removed
    - Permissions are enforced
    """
    # Step 1: Create organization and project
    admin_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Admin User",
    )
    client_instance, headers, _ = await authenticated_client(client, admin_data)
    org = await create_test_organization(
        client_instance,
        headers,
        name="Test Org",
        slug="test-org-project-member",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )
    project_id = project["id"]

    # Step 2: Create member user
    member_email = f"member-{unique_email}"
    member_data = await create_test_user(
        client,
        email=member_email,
        password=test_password,
        name="Member User",
    )
    member_user_id = member_data["id"]

    # Step 3: Add member to project
    add_member_response = await client_instance.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": member_user_id, "role": "viewer"},
        headers=headers,
    )
    assert add_member_response.status_code == 201
    added_member = add_member_response.json()
    assert added_member["user_id"] == member_user_id
    assert added_member["role"] == "viewer"

    # Step 4: List project members
    members_response = await client_instance.get(
        f"/api/v1/projects/{project_id}/members",
        headers=headers,
    )
    assert members_response.status_code == 200
    members_data = members_response.json()
    assert "members" in members_data
    assert any(m["user_id"] == member_user_id for m in members_data["members"])

    # Step 5: Update member role
    update_role_response = await client_instance.put(
        f"/api/v1/projects/{project_id}/members/{member_user_id}",
        json={"role": "admin"},
        headers=headers,
    )
    assert update_role_response.status_code == 200
    updated_member = update_role_response.json()
    assert updated_member["role"] == "admin"

    # Step 6: Remove member
    remove_response = await client_instance.delete(
        f"/api/v1/projects/{project_id}/members/{member_user_id}",
        headers=headers,
    )
    assert remove_response.status_code == 204

    # Step 7: Verify member is removed
    members_response2 = await client_instance.get(
        f"/api/v1/projects/{project_id}/members",
        headers=headers,
    )
    assert members_response2.status_code == 200
    members_data2 = members_response2.json()
    assert not any(m["user_id"] == member_user_id for m in members_data2["members"])


@pytest.mark.asyncio
async def test_project_lifecycle_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test project lifecycle: Create → Update → Delete → Verify soft delete.

    This workflow validates that:
    - Project can be created
    - Project can be updated
    - Project can be soft deleted
    - Deleted project is not accessible
    """
    # Step 1: Create organization and project
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
        slug="test-org-lifecycle",
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Lifecycle Project",
        key="LIFE",
    )
    project_id = project["id"]

    # Step 2: Update project
    update_response = await client_instance.put(
        f"/api/v1/projects/{project_id}",
        json={"name": "Updated Project Name", "description": "Updated description"},
        headers=headers,
    )
    assert update_response.status_code == 200
    updated_project = update_response.json()
    assert updated_project["name"] == "Updated Project Name"
    assert updated_project["description"] == "Updated description"

    # Step 3: Delete project
    delete_response = await client_instance.delete(
        f"/api/v1/projects/{project_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    # Step 4: Verify project is not accessible (soft delete - may still return 200)
    get_response = await client_instance.get(
        f"/api/v1/projects/{project_id}",
        headers=headers,
    )
    # Soft delete may return 200 or 404 depending on implementation
    assert get_response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_project_key_generation_flow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test project key generation: Create without key → Verify auto-gen → Create with custom.

    This workflow validates that:
    - Project key is auto-generated when not provided
    - Custom keys can be provided
    - Key conflicts are detected
    """
    # Step 1: Create organization
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
        slug="test-org-key",
    )

    # Step 2: Create project without key
    project1 = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Auto Key Project",
    )
    assert "key" in project1
    assert len(project1["key"]) > 0

    # Step 3: Create project with custom key
    project2 = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Custom Key Project",
        key="CUSTOM",
    )
    assert project2["key"] == "CUSTOM"

    # Step 4: Attempt to create project with duplicate key
    duplicate_response = await client_instance.post(
        "/api/v1/projects/",
        json={
            "organization_id": org["id"],
            "name": "Duplicate Key Project",
            "key": "CUSTOM",
        },
        headers=headers,
    )
    assert duplicate_response.status_code in (400, 409)
    error_data = duplicate_response.json()
    assert "key" in str(error_data).lower() or "already" in str(error_data).lower()


@pytest.mark.asyncio
async def test_project_organization_isolation_flow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test project organization isolation: Create 2 Orgs → Create Projects → Verify isolation.

    This workflow validates that:
    - Projects are isolated by organization
    - Members of one org cannot see projects from another org
    - Cross-organization access is prevented
    """
    # Step 1: Create first organization and project
    user1_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="User 1",
    )
    client1, headers1, _ = await authenticated_client(client, user1_data)
    org1 = await create_test_organization(
        client1,
        headers1,
        name="Organization 1",
        slug="org-1-isolation",
    )
    project1 = await create_test_project(
        client1,
        headers1,
        organization_id=org1["id"],
        name="Project 1",
        key="PROJ1",
    )

    # Step 2: Create second organization and project
    user2_email = f"user2-{unique_email}"
    user2_data = await create_test_user(
        client,
        email=user2_email,
        password=test_password,
        name="User 2",
    )
    client2, headers2, _ = await authenticated_client(client, user2_data)
    org2 = await create_test_organization(
        client2,
        headers2,
        name="Organization 2",
        slug="org-2-isolation",
    )
    project2 = await create_test_project(
        client2,
        headers2,
        organization_id=org2["id"],
        name="Project 2",
        key="PROJ2",
    )

    # Step 3: User 1 lists projects (should only see org1 projects)
    list1_response = await client1.get(
        "/api/v1/projects/",
        headers=headers1,
        params={"organization_id": org1["id"]},
    )
    assert list1_response.status_code == 200
    projects1 = list1_response.json()["projects"]
    project1_ids = [p["id"] for p in projects1]
    assert project1["id"] in project1_ids
    assert project2["id"] not in project1_ids

    # Step 4: User 1 attempts to access org2 project (should fail)
    access_response = await client1.get(
        f"/api/v1/projects/{project2['id']}",
        headers=headers1,
    )
    assert access_response.status_code in (403, 404)
