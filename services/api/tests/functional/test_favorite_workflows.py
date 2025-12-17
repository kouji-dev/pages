"""Functional tests for favorite workflows."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    PageModel,
    ProjectModel,
    SpaceModel,
)


@pytest.mark.asyncio
async def test_favorite_workflow_create_list_delete(client: AsyncClient, test_user, db_session):
    """Test complete favorite workflow: create, list, delete."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="member",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Create project, space, and page
    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    space = SpaceModel(
        organization_id=org.id,
        name="Test Space",
        key="TEST",
    )
    db_session.add(project)
    db_session.add(space)
    await db_session.flush()

    page = PageModel(
        space_id=space.id,
        title="Test Page",
        slug="test-page",
        content="Content",
    )
    db_session.add(page)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 1. Create favorite for project
    create_project_fav_response = await client.post(
        "/api/v1/users/me/favorites",
        json={
            "entity_type": "project",
            "entity_id": str(project.id),
        },
        headers=auth_headers,
    )
    assert create_project_fav_response.status_code == 201
    project_fav_data = create_project_fav_response.json()
    project_fav_id = project_fav_data["id"]
    assert project_fav_data["entity_type"] == "project"
    assert project_fav_data["entity_id"] == str(project.id)

    # 2. Create favorite for space
    create_space_fav_response = await client.post(
        "/api/v1/users/me/favorites",
        json={
            "entity_type": "space",
            "entity_id": str(space.id),
        },
        headers=auth_headers,
    )
    assert create_space_fav_response.status_code == 201
    space_fav_data = create_space_fav_response.json()
    assert space_fav_data["entity_type"] == "space"

    # 3. Create favorite for page
    create_page_fav_response = await client.post(
        "/api/v1/users/me/favorites",
        json={
            "entity_type": "page",
            "entity_id": str(page.id),
        },
        headers=auth_headers,
    )
    assert create_page_fav_response.status_code == 201
    page_fav_data = create_page_fav_response.json()
    assert page_fav_data["entity_type"] == "page"

    # 4. List all favorites
    list_all_response = await client.get(
        "/api/v1/users/me/favorites",
        headers=auth_headers,
    )
    assert list_all_response.status_code == 200
    list_all_data = list_all_response.json()
    assert list_all_data["total"] == 3
    assert len(list_all_data["favorites"]) == 3
    entity_types = [f["entity_type"] for f in list_all_data["favorites"]]
    assert "project" in entity_types
    assert "space" in entity_types
    assert "page" in entity_types

    # 5. List favorites filtered by entity type (project)
    list_projects_response = await client.get(
        "/api/v1/users/me/favorites",
        params={"entity_type": "project"},
        headers=auth_headers,
    )
    assert list_projects_response.status_code == 200
    list_projects_data = list_projects_response.json()
    assert list_projects_data["total"] == 1
    assert list_projects_data["favorites"][0]["entity_type"] == "project"

    # 6. List favorites filtered by entity type (space)
    list_spaces_response = await client.get(
        "/api/v1/users/me/favorites",
        params={"entity_type": "space"},
        headers=auth_headers,
    )
    assert list_spaces_response.status_code == 200
    list_spaces_data = list_spaces_response.json()
    assert list_spaces_data["total"] == 1
    assert list_spaces_data["favorites"][0]["entity_type"] == "space"

    # 7. Delete project favorite
    delete_project_fav_response = await client.delete(
        f"/api/v1/users/me/favorites/{project_fav_id}",
        headers=auth_headers,
    )
    assert delete_project_fav_response.status_code == 204

    # 8. Verify favorite is deleted
    list_after_delete_response = await client.get(
        "/api/v1/users/me/favorites",
        headers=auth_headers,
    )
    assert list_after_delete_response.status_code == 200
    list_after_delete_data = list_after_delete_response.json()
    assert list_after_delete_data["total"] == 2
    remaining_types = [f["entity_type"] for f in list_after_delete_data["favorites"]]
    assert "project" not in remaining_types
    assert "space" in remaining_types
    assert "page" in remaining_types

    # 9. Try to create duplicate favorite (should fail)
    duplicate_response = await client.post(
        "/api/v1/users/me/favorites",
        json={
            "entity_type": "space",
            "entity_id": str(space.id),
        },
        headers=auth_headers,
    )
    assert duplicate_response.status_code == 409


@pytest.mark.asyncio
async def test_favorite_heterogeneous_list_workflow(client: AsyncClient, test_user, db_session):
    """Test workflow for managing heterogeneous favorites list."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="member",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Create multiple projects, spaces, and pages
    projects = [
        ProjectModel(
            organization_id=org.id,
            name=f"Project {i}",
            key=f"PROJ{i}",
        )
        for i in range(3)
    ]
    spaces = [
        SpaceModel(
            organization_id=org.id,
            name=f"Space {i}",
            key=f"SPACE{i}",
        )
        for i in range(2)
    ]
    db_session.add_all(projects)
    db_session.add_all(spaces)
    await db_session.flush()

    pages = [
        PageModel(
            space_id=spaces[0].id,
            title=f"Page {i}",
            slug=f"page-{i}",
            content="Content",
        )
        for i in range(2)
    ]
    db_session.add_all(pages)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create favorites for all entities
    favorite_ids = []
    for project in projects:
        response = await client.post(
            "/api/v1/users/me/favorites",
            json={
                "entity_type": "project",
                "entity_id": str(project.id),
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        favorite_ids.append(response.json()["id"])

    for space in spaces:
        response = await client.post(
            "/api/v1/users/me/favorites",
            json={
                "entity_type": "space",
                "entity_id": str(space.id),
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        favorite_ids.append(response.json()["id"])

    for page in pages:
        response = await client.post(
            "/api/v1/users/me/favorites",
            json={
                "entity_type": "page",
                "entity_id": str(page.id),
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        favorite_ids.append(response.json()["id"])

    # List all favorites (should have 7 total: 3 projects + 2 spaces + 2 pages)
    list_all_response = await client.get(
        "/api/v1/users/me/favorites",
        headers=auth_headers,
    )
    assert list_all_response.status_code == 200
    list_all_data = list_all_response.json()
    assert list_all_data["total"] == 7

    # Verify distribution
    entity_type_counts = {}
    for fav in list_all_data["favorites"]:
        entity_type = fav["entity_type"]
        entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1

    assert entity_type_counts["project"] == 3
    assert entity_type_counts["space"] == 2
    assert entity_type_counts["page"] == 2

    # Delete all favorites
    for fav_id in favorite_ids:
        delete_response = await client.delete(
            f"/api/v1/users/me/favorites/{fav_id}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 204

    # Verify all favorites are deleted
    list_empty_response = await client.get(
        "/api/v1/users/me/favorites",
        headers=auth_headers,
    )
    assert list_empty_response.status_code == 200
    assert list_empty_response.json()["total"] == 0
