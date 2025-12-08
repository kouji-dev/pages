"""Functional tests for permissions and security workflows."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    authenticated_client,
    create_test_issue,
    create_test_organization,
    create_test_page,
    create_test_project,
    create_test_space,
    create_test_user,
    get_auth_headers,
    get_user_id,
)


@pytest.mark.asyncio
async def test_admin_permissions_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test admin permissions workflow: Admin actions should all work.

    This workflow validates that:
    - Admin can create organization
    - Admin can add members
    - Admin can update settings
    - Admin can delete organization
    """
    # Step 1: Create admin user and organization
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
        slug="test-org-admin",
    )
    org_id = org["id"]

    # Step 2: Admin can add member
    member_email = f"member-{unique_email}"
    member_data = await create_test_user(
        client,
        email=member_email,
        password=test_password,
        name="Member User",
    )
    add_member_response = await client_instance.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": member_data["id"], "role": "member"},
        headers=headers,
    )
    assert add_member_response.status_code == 201

    # Step 3: Admin can update settings
    update_settings_response = await client_instance.put(
        f"/api/v1/organizations/{org_id}/settings",
        json={"settings": {"notifications": {"email_digest_frequency": "daily"}}},
        headers=headers,
    )
    assert update_settings_response.status_code == 200

    # Step 4: Admin can delete organization
    delete_response = await client_instance.delete(
        f"/api/v1/organizations/{org_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_member_permissions_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test member permissions workflow: Member cannot perform admin actions.

    This workflow validates that:
    - Member cannot add members
    - Member cannot update settings
    - Member cannot delete organization
    - Member can perform allowed actions
    """
    # Step 1: Create admin and organization
    admin_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Admin User",
    )
    admin_client, admin_headers, _ = await authenticated_client(client, admin_data)
    org = await create_test_organization(
        admin_client,
        admin_headers,
        name="Test Org",
        slug="test-org-member-perms",
    )
    org_id = org["id"]

    # Step 2: Add member to organization
    member_email = f"member-{unique_email}"
    member_data = await create_test_user(
        client,
        email=member_email,
        password=test_password,
        name="Member User",
    )
    add_member_response = await admin_client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": member_data["id"], "role": "member"},
        headers=admin_headers,
    )
    assert add_member_response.status_code == 201

    # Step 3: Member attempts admin actions (should fail)
    member_client, member_headers, _ = await authenticated_client(client, member_data)

    # Member cannot add other members
    another_user_data = await create_test_user(
        client,
        email=f"another-{unique_email}",
        password=test_password,
        name="Another User",
    )
    add_member_attempt = await member_client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": another_user_data["id"], "role": "member"},
        headers=member_headers,
    )
    assert add_member_attempt.status_code == 403

    # Member cannot update settings
    update_settings_attempt = await member_client.put(
        f"/api/v1/organizations/{org_id}/settings",
        json={"settings": {"notifications": {"email_digest_frequency": "weekly"}}},
        headers=member_headers,
    )
    assert update_settings_attempt.status_code == 403

    # Member cannot delete organization
    delete_attempt = await member_client.delete(
        f"/api/v1/organizations/{org_id}",
        headers=member_headers,
    )
    assert delete_attempt.status_code == 403

    # Step 4: Member can perform allowed actions (view organization)
    view_org_response = await member_client.get(
        f"/api/v1/organizations/{org_id}",
        headers=member_headers,
    )
    assert view_org_response.status_code == 200


@pytest.mark.asyncio
async def test_project_permissions_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test project permissions workflow: Viewer cannot edit, member can edit.

    This workflow validates that:
    - Project viewer cannot edit issues
    - Project member can edit issues
    - Role updates change permissions
    """
    # Step 1: Create organization and project
    admin_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Admin User",
    )
    admin_client, admin_headers, _ = await authenticated_client(client, admin_data)
    org = await create_test_organization(
        admin_client,
        admin_headers,
        name="Test Org",
        slug="test-org-project-perms",
    )
    project = await create_test_project(
        admin_client,
        admin_headers,
        organization_id=org["id"],
        name="Test Project",
        key="TEST",
    )

    # Step 2: Add member to organization first (as viewer to test project-level permissions)
    member_email = f"member-{unique_email}"
    member_data = await create_test_user(
        client,
        email=member_email,
        password=test_password,
        name="Member User",
    )
    # Add member to organization as viewer (so organization role doesn't grant edit permission)
    await admin_client.post(
        f"/api/v1/organizations/{org['id']}/members",
        json={"user_id": member_data["id"], "role": "viewer"},
        headers=admin_headers,
    )

    # Step 3: Add member as viewer to project
    add_member_response = await admin_client.post(
        f"/api/v1/projects/{project['id']}/members",
        json={"user_id": member_data["id"], "role": "viewer"},
        headers=admin_headers,
    )
    assert add_member_response.status_code == 201

    # Step 4: Create issue as admin
    issue = await create_test_issue(
        admin_client,
        admin_headers,
        project_id=project["id"],
        title="Test Issue",
    )

    # Step 5: Member (viewer) attempts to edit issue (should fail)
    member_client, member_headers, _ = await authenticated_client(client, member_data)
    edit_attempt = await member_client.put(
        f"/api/v1/issues/{issue['id']}",
        json={"status": "in_progress"},
        headers=member_headers,
    )
    assert edit_attempt.status_code == 403

    # Step 6: Update member role to member (which allows editing)
    update_role_response = await admin_client.put(
        f"/api/v1/projects/{project['id']}/members/{member_data['id']}",
        json={"role": "member"},
        headers=admin_headers,
    )
    assert update_role_response.status_code == 200

    # Step 7: Member (now member role) can edit issue
    edit_success = await member_client.put(
        f"/api/v1/issues/{issue['id']}",
        json={"status": "in_progress"},
        headers=member_headers,
    )
    assert edit_success.status_code == 200


@pytest.mark.asyncio
async def test_cross_organization_isolation_flow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test cross-organization isolation: Users cannot access other orgs' resources.

    This workflow validates that:
    - User1 cannot access User2's organization
    - User1 cannot access User2's projects
    - Cross-organization access is prevented
    """
    # Step 1: User1 creates organization and project
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

    # Step 2: User2 creates organization and project
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

    # Step 3: User1 attempts to access User2's organization (should fail)
    access_org2_response = await client1.get(
        f"/api/v1/organizations/{org2['id']}",
        headers=headers1,
    )
    assert access_org2_response.status_code in (403, 404)

    # Step 4: User1 attempts to access User2's project (should fail)
    access_project2_response = await client1.get(
        f"/api/v1/projects/{project2['id']}",
        headers=headers1,
    )
    assert access_project2_response.status_code in (403, 404)

    # Step 5: User1 can access own resources
    access_org1_response = await client1.get(
        f"/api/v1/organizations/{org1['id']}",
        headers=headers1,
    )
    assert access_org1_response.status_code == 200

    access_project1_response = await client1.get(
        f"/api/v1/projects/{project1['id']}",
        headers=headers1,
    )
    assert access_project1_response.status_code == 200


@pytest.mark.asyncio
async def test_token_authentication_flow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test token authentication flow: Valid token works, invalid/expired tokens are rejected.

    This workflow validates that:
    - Valid access token allows access
    - Invalid token is rejected
    - Missing token is rejected
    """
    # Step 1: Register and login
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    client_instance, headers, _ = await authenticated_client(client, user_data)

    # Step 2: Valid token works
    profile_response = await client_instance.get(
        "/api/v1/users/me",
        headers=headers,
    )
    assert profile_response.status_code == 200

    # Step 3: Invalid token is rejected
    invalid_headers = get_auth_headers("invalid.token.here")
    invalid_response = await client_instance.get(
        "/api/v1/users/me",
        headers=invalid_headers,
    )
    assert invalid_response.status_code == 401

    # Step 4: Missing token is rejected
    no_auth_response = await client_instance.get(
        "/api/v1/users/me",
    )
    assert no_auth_response.status_code == 401

    # Step 5: Malformed token is rejected
    malformed_headers = {"Authorization": "Bearer not.a.valid.jwt.token"}
    malformed_response = await client_instance.get(
        "/api/v1/users/me",
        headers=malformed_headers,
    )
    assert malformed_response.status_code == 401


@pytest.mark.asyncio
async def test_viewer_cannot_create_issue(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test that viewers cannot create issues.

    This workflow validates that:
    - Viewer role cannot create issues
    - Only members/admins can create issues
    """
    # Step 1: Create admin and viewer users, organization and project
    admin_email = f"admin-{unique_email}"
    admin_data = await create_test_user(
        client,
        email=admin_email,
        password=test_password,
        name="Admin User",
    )
    admin_client, admin_headers, _ = await authenticated_client(client, admin_data)
    org = await create_test_organization(
        admin_client,
        admin_headers,
        name="Viewer Test Org",
        slug="viewer-test-org",
    )
    org_id = org["id"]
    project = await create_test_project(
        admin_client,
        admin_headers,
        organization_id=org_id,
        name="Viewer Test Project",
        key="VIEW",
    )
    project_id = project["id"]

    viewer_email = f"viewer-{unique_email}"
    viewer_data = await create_test_user(
        client,
        email=viewer_email,
        password=test_password,
        name="Viewer User",
    )
    viewer_user_id = get_user_id(viewer_data)

    # Add viewer to organization as viewer
    await admin_client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Add viewer to project as viewer
    await admin_client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Step 2: Viewer attempts to create an issue (should fail)
    viewer_client, viewer_headers, _ = await authenticated_client(client, viewer_data)
    create_issue_response = await viewer_client.post(
        "/api/v1/issues/",
        json={"project_id": project_id, "title": "Viewer Created Issue"},
        headers=viewer_headers,
    )
    assert create_issue_response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_viewer_cannot_update_issue(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test that viewers cannot update issues.

    This workflow validates that:
    - Viewer role cannot update issues
    - Only members/admins can update issues
    """
    # Step 1: Create admin and viewer users, organization, project and issue
    admin_email = f"admin-{unique_email}"
    admin_data = await create_test_user(
        client,
        email=admin_email,
        password=test_password,
        name="Admin User",
    )
    admin_client, admin_headers, _ = await authenticated_client(client, admin_data)
    org = await create_test_organization(
        admin_client,
        admin_headers,
        name="Viewer Update Org",
        slug="viewer-update-org",
    )
    org_id = org["id"]
    project = await create_test_project(
        admin_client,
        admin_headers,
        organization_id=org_id,
        name="Viewer Update Project",
        key="VUPD",
    )
    project_id = project["id"]
    issue = await create_test_issue(
        admin_client,
        admin_headers,
        project_id=project_id,
        title="Issue to Update",
    )
    issue_id = issue["id"]

    viewer_email = f"viewer-{unique_email}"
    viewer_data = await create_test_user(
        client,
        email=viewer_email,
        password=test_password,
        name="Viewer User",
    )
    viewer_user_id = get_user_id(viewer_data)

    # Add viewer to organization as viewer
    await admin_client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Add viewer to project as viewer
    await admin_client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Step 2: Viewer attempts to update the issue (should fail)
    viewer_client, viewer_headers, _ = await authenticated_client(client, viewer_data)
    update_issue_response = await viewer_client.put(
        f"/api/v1/issues/{issue_id}",
        json={"status": "in_progress"},
        headers=viewer_headers,
    )
    assert update_issue_response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_viewer_cannot_delete_issue(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test that viewers cannot delete issues.

    This workflow validates that:
    - Viewer role cannot delete issues
    - Only members/admins can delete issues
    """
    # Step 1: Create admin and viewer users, organization, project and issue
    admin_email = f"admin-{unique_email}"
    admin_data = await create_test_user(
        client,
        email=admin_email,
        password=test_password,
        name="Admin User",
    )
    admin_client, admin_headers, _ = await authenticated_client(client, admin_data)
    org = await create_test_organization(
        admin_client,
        admin_headers,
        name="Viewer Delete Org",
        slug="viewer-delete-org",
    )
    org_id = org["id"]
    project = await create_test_project(
        admin_client,
        admin_headers,
        organization_id=org_id,
        name="Viewer Delete Project",
        key="VDEL",
    )
    project_id = project["id"]
    issue = await create_test_issue(
        admin_client,
        admin_headers,
        project_id=project_id,
        title="Issue to Delete",
    )
    issue_id = issue["id"]

    viewer_email = f"viewer-{unique_email}"
    viewer_data = await create_test_user(
        client,
        email=viewer_email,
        password=test_password,
        name="Viewer User",
    )
    viewer_user_id = get_user_id(viewer_data)

    # Add viewer to organization as viewer
    await admin_client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Add viewer to project as viewer
    await admin_client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Step 2: Viewer attempts to delete the issue (should fail)
    viewer_client, viewer_headers, _ = await authenticated_client(client, viewer_data)
    delete_issue_response = await viewer_client.delete(
        f"/api/v1/issues/{issue_id}",
        headers=viewer_headers,
    )
    assert delete_issue_response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_viewer_cannot_create_page(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test that viewers cannot create pages.

    This workflow validates that:
    - Viewer role cannot create pages
    - Only members/admins can create pages
    """
    # Step 1: Create admin and viewer users, organization and space
    admin_email = f"admin-{unique_email}"
    admin_data = await create_test_user(
        client,
        email=admin_email,
        password=test_password,
        name="Admin User",
    )
    admin_client, admin_headers, _ = await authenticated_client(client, admin_data)
    org = await create_test_organization(
        admin_client,
        admin_headers,
        name="Viewer Page Org",
        slug="viewer-page-org",
    )
    org_id = org["id"]
    space = await create_test_space(
        admin_client,
        admin_headers,
        organization_id=org_id,
        name="Viewer Test Space",
        key="VIEW",
    )
    space_id = space["id"]

    viewer_email = f"viewer-{unique_email}"
    viewer_data = await create_test_user(
        client,
        email=viewer_email,
        password=test_password,
        name="Viewer User",
    )
    viewer_user_id = get_user_id(viewer_data)

    # Add viewer to organization as viewer
    await admin_client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Step 2: Viewer attempts to create a page (should fail)
    viewer_client, viewer_headers, _ = await authenticated_client(client, viewer_data)
    create_page_response = await viewer_client.post(
        "/api/v1/pages/",
        json={"space_id": space_id, "title": "Viewer Created Page"},
        headers=viewer_headers,
    )
    assert create_page_response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_viewer_cannot_update_page(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test that viewers cannot update pages.

    This workflow validates that:
    - Viewer role cannot update pages
    - Only members/admins can update pages
    """
    # Step 1: Create admin and viewer users, organization, space and page
    admin_email = f"admin-{unique_email}"
    admin_data = await create_test_user(
        client,
        email=admin_email,
        password=test_password,
        name="Admin User",
    )
    admin_client, admin_headers, _ = await authenticated_client(client, admin_data)
    org = await create_test_organization(
        admin_client,
        admin_headers,
        name="Viewer Page Update Org",
        slug="viewer-page-update-org",
    )
    org_id = org["id"]
    space = await create_test_space(
        admin_client,
        admin_headers,
        organization_id=org_id,
        name="Viewer Update Space",
        key="VUPD",
    )
    space_id = space["id"]
    page = await create_test_page(
        admin_client,
        admin_headers,
        space_id=space_id,
        title="Page to Update",
    )
    page_id = page["id"]

    viewer_email = f"viewer-{unique_email}"
    viewer_data = await create_test_user(
        client,
        email=viewer_email,
        password=test_password,
        name="Viewer User",
    )
    viewer_user_id = get_user_id(viewer_data)

    # Add viewer to organization as viewer
    await admin_client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Step 2: Viewer attempts to update the page (should fail)
    viewer_client, viewer_headers, _ = await authenticated_client(client, viewer_data)
    update_page_response = await viewer_client.put(
        f"/api/v1/pages/{page_id}",
        json={"title": "Updated by Viewer"},
        headers=viewer_headers,
    )
    assert update_page_response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_viewer_cannot_create_project(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test that viewers cannot create projects.

    This workflow validates that:
    - Viewer role cannot create projects
    - Only members/admins can create projects
    """
    # Step 1: Create admin and viewer users, organization
    admin_email = f"admin-{unique_email}"
    admin_data = await create_test_user(
        client,
        email=admin_email,
        password=test_password,
        name="Admin User",
    )
    admin_client, admin_headers, _ = await authenticated_client(client, admin_data)
    org = await create_test_organization(
        admin_client,
        admin_headers,
        name="Viewer Project Org",
        slug="viewer-project-org",
    )
    org_id = org["id"]

    viewer_email = f"viewer-{unique_email}"
    viewer_data = await create_test_user(
        client,
        email=viewer_email,
        password=test_password,
        name="Viewer User",
    )
    viewer_user_id = get_user_id(viewer_data)

    # Add viewer to organization as viewer
    await admin_client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Step 2: Viewer attempts to create a project (should fail)
    viewer_client, viewer_headers, _ = await authenticated_client(client, viewer_data)
    create_project_response = await viewer_client.post(
        "/api/v1/projects/",
        json={"organization_id": org_id, "name": "Viewer Created Project", "key": "VCP"},
        headers=viewer_headers,
    )
    assert create_project_response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_viewer_cannot_update_project(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test that viewers cannot update projects.

    This workflow validates that:
    - Viewer role cannot update projects
    - Only members/admins can update projects
    """
    # Step 1: Create admin and viewer users, organization and project
    admin_email = f"admin-{unique_email}"
    admin_data = await create_test_user(
        client,
        email=admin_email,
        password=test_password,
        name="Admin User",
    )
    admin_client, admin_headers, _ = await authenticated_client(client, admin_data)
    org = await create_test_organization(
        admin_client,
        admin_headers,
        name="Viewer Project Update Org",
        slug="viewer-project-update-org",
    )
    org_id = org["id"]
    project = await create_test_project(
        admin_client,
        admin_headers,
        organization_id=org_id,
        name="Viewer Update Project",
        key="VUPD",
    )
    project_id = project["id"]

    viewer_email = f"viewer-{unique_email}"
    viewer_data = await create_test_user(
        client,
        email=viewer_email,
        password=test_password,
        name="Viewer User",
    )
    viewer_user_id = get_user_id(viewer_data)

    # Add viewer to organization as viewer
    await admin_client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Step 2: Viewer attempts to update the project (should fail)
    viewer_client, viewer_headers, _ = await authenticated_client(client, viewer_data)
    update_project_response = await viewer_client.put(
        f"/api/v1/projects/{project_id}",
        json={"name": "Updated by Viewer"},
        headers=viewer_headers,
    )
    assert update_project_response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_viewer_cannot_create_space(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test that viewers cannot create spaces.

    This workflow validates that:
    - Viewer role cannot create spaces
    - Only members/admins can create spaces
    """
    # Step 1: Create admin and viewer users, organization
    admin_email = f"admin-{unique_email}"
    admin_data = await create_test_user(
        client,
        email=admin_email,
        password=test_password,
        name="Admin User",
    )
    admin_client, admin_headers, _ = await authenticated_client(client, admin_data)
    org = await create_test_organization(
        admin_client,
        admin_headers,
        name="Viewer Space Org",
        slug="viewer-space-org",
    )
    org_id = org["id"]

    viewer_email = f"viewer-{unique_email}"
    viewer_data = await create_test_user(
        client,
        email=viewer_email,
        password=test_password,
        name="Viewer User",
    )
    viewer_user_id = get_user_id(viewer_data)

    # Add viewer to organization as viewer
    await admin_client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Step 2: Viewer attempts to create a space (should fail)
    viewer_client, viewer_headers, _ = await authenticated_client(client, viewer_data)
    create_space_response = await viewer_client.post(
        "/api/v1/spaces/",
        json={"organization_id": org_id, "name": "Viewer Created Space", "key": "VCS"},
        headers=viewer_headers,
    )
    assert create_space_response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_viewer_cannot_create_template(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test that viewers cannot create templates.

    This workflow validates that:
    - Viewer role cannot create templates
    - Only members/admins can create templates
    """
    # Step 1: Create admin and viewer users, organization
    admin_email = f"admin-{unique_email}"
    admin_data = await create_test_user(
        client,
        email=admin_email,
        password=test_password,
        name="Admin User",
    )
    admin_client, admin_headers, _ = await authenticated_client(client, admin_data)
    org = await create_test_organization(
        admin_client,
        admin_headers,
        name="Viewer Template Org",
        slug="viewer-template-org",
    )
    org_id = org["id"]

    viewer_email = f"viewer-{unique_email}"
    viewer_data = await create_test_user(
        client,
        email=viewer_email,
        password=test_password,
        name="Viewer User",
    )
    viewer_user_id = get_user_id(viewer_data)

    # Add viewer to organization as viewer
    await admin_client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Step 2: Viewer attempts to create a template (should fail)
    viewer_client, viewer_headers, _ = await authenticated_client(client, viewer_data)
    create_template_response = await viewer_client.post(
        "/api/v1/templates/",
        json={
            "organization_id": org_id,
            "name": "Viewer Created Template",
            "content": "# Template",
        },
        headers=viewer_headers,
    )
    assert create_template_response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_viewer_cannot_create_comment(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test that viewers cannot create comments.

    This workflow validates that:
    - Viewer role cannot create comments
    - Only members/admins can create comments
    """
    # Step 1: Create admin and viewer users, organization, project and issue
    admin_email = f"admin-{unique_email}"
    admin_data = await create_test_user(
        client,
        email=admin_email,
        password=test_password,
        name="Admin User",
    )
    admin_client, admin_headers, _ = await authenticated_client(client, admin_data)
    org = await create_test_organization(
        admin_client,
        admin_headers,
        name="Viewer Comment Org",
        slug="viewer-comment-org",
    )
    org_id = org["id"]
    project = await create_test_project(
        admin_client,
        admin_headers,
        organization_id=org_id,
        name="Viewer Comment Project",
        key="VCOM",
    )
    project_id = project["id"]
    issue = await create_test_issue(
        admin_client,
        admin_headers,
        project_id=project_id,
        title="Issue for Comments",
    )
    issue_id = issue["id"]

    viewer_email = f"viewer-{unique_email}"
    viewer_data = await create_test_user(
        client,
        email=viewer_email,
        password=test_password,
        name="Viewer User",
    )
    viewer_user_id = get_user_id(viewer_data)

    # Add viewer to organization as viewer
    await admin_client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Add viewer to project as viewer
    await admin_client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Step 2: Viewer attempts to create a comment (should fail)
    viewer_client, viewer_headers, _ = await authenticated_client(client, viewer_data)
    create_comment_response = await viewer_client.post(
        f"/api/v1/issues/{issue_id}/comments",
        json={"content": "Viewer comment"},
        headers=viewer_headers,
    )
    assert create_comment_response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_viewer_cannot_upload_attachment(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test that viewers cannot upload attachments.

    This workflow validates that:
    - Viewer role cannot upload attachments
    - Only members/admins can upload attachments
    """
    # Step 1: Create admin and viewer users, organization, project and issue
    admin_email = f"admin-{unique_email}"
    admin_data = await create_test_user(
        client,
        email=admin_email,
        password=test_password,
        name="Admin User",
    )
    admin_client, admin_headers, _ = await authenticated_client(client, admin_data)
    org = await create_test_organization(
        admin_client,
        admin_headers,
        name="Viewer Attachment Org",
        slug="viewer-attachment-org",
    )
    org_id = org["id"]
    project = await create_test_project(
        admin_client,
        admin_headers,
        organization_id=org_id,
        name="Viewer Attachment Project",
        key="VATT",
    )
    project_id = project["id"]
    issue = await create_test_issue(
        admin_client,
        admin_headers,
        project_id=project_id,
        title="Issue for Attachments",
    )
    issue_id = issue["id"]

    viewer_email = f"viewer-{unique_email}"
    viewer_data = await create_test_user(
        client,
        email=viewer_email,
        password=test_password,
        name="Viewer User",
    )
    viewer_user_id = get_user_id(viewer_data)

    # Add viewer to organization as viewer
    await admin_client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Add viewer to project as viewer
    await admin_client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": viewer_user_id, "role": "viewer"},
        headers=admin_headers,
    )

    # Step 2: Viewer attempts to upload an attachment (should fail)
    viewer_client, viewer_headers, _ = await authenticated_client(client, viewer_data)
    # Create a simple test file
    import io

    test_file_content = b"Test file content"
    files = {"file": ("test.txt", io.BytesIO(test_file_content), "text/plain")}
    upload_attachment_response = await viewer_client.post(
        f"/api/v1/issues/{issue_id}/attachments",
        files=files,
        headers=viewer_headers,
    )
    assert upload_attachment_response.status_code == 403  # Forbidden
