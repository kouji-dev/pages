"""Integration tests for favorite endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    FavoriteModel,
    OrganizationMemberModel,
    OrganizationModel,
    ProjectModel,
    SpaceModel,
)


@pytest.mark.asyncio
async def test_create_favorite_project_success(client: AsyncClient, test_user, db_session):
    """Test successful favorite creation for project."""
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

    # Create project
    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    # Login to get token
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

    # Create favorite
    create_response = await client.post(
        "/api/v1/users/me/favorites",
        json={
            "entity_type": "project",
            "entity_id": str(project.id),
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["entity_type"] == "project"
    assert data["entity_id"] == str(project.id)
    assert data["user_id"] == str(test_user.id)
    assert "id" in data


@pytest.mark.asyncio
async def test_create_favorite_space_success(client: AsyncClient, test_user, db_session):
    """Test successful favorite creation for space."""
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

    # Create space
    space = SpaceModel(
        organization_id=org.id,
        name="Test Space",
        key="TEST",
    )
    db_session.add(space)
    await db_session.flush()

    # Login to get token
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

    # Create favorite
    create_response = await client.post(
        "/api/v1/users/me/favorites",
        json={
            "entity_type": "space",
            "entity_id": str(space.id),
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["entity_type"] == "space"
    assert data["entity_id"] == str(space.id)


@pytest.mark.asyncio
async def test_create_favorite_duplicate(client: AsyncClient, test_user, db_session):
    """Test favorite creation with duplicate favorite."""
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

    # Create project
    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    # Create existing favorite
    favorite = FavoriteModel(
        user_id=test_user.id,
        entity_type="project",
        entity_id=project.id,
    )
    db_session.add(favorite)
    await db_session.flush()

    # Login to get token
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

    # Try to create duplicate favorite
    create_response = await client.post(
        "/api/v1/users/me/favorites",
        json={
            "entity_type": "project",
            "entity_id": str(project.id),
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 409


@pytest.mark.asyncio
async def test_list_favorites_success(client: AsyncClient, test_user, db_session):
    """Test successful favorite listing."""
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

    # Create project and space
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

    # Create favorites
    favorite1 = FavoriteModel(
        user_id=test_user.id,
        entity_type="project",
        entity_id=project.id,
    )
    favorite2 = FavoriteModel(
        user_id=test_user.id,
        entity_type="space",
        entity_id=space.id,
    )
    db_session.add(favorite1)
    db_session.add(favorite2)
    await db_session.flush()

    # Login to get token
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

    # List favorites
    list_response = await client.get(
        "/api/v1/users/me/favorites",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 2
    assert len(data["favorites"]) == 2
    entity_types = [f["entity_type"] for f in data["favorites"]]
    assert "project" in entity_types
    assert "space" in entity_types


@pytest.mark.asyncio
async def test_list_favorites_with_entity_type_filter(client: AsyncClient, test_user, db_session):
    """Test favorite listing with entity type filter."""
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

    # Create project and space
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

    # Create favorites
    favorite1 = FavoriteModel(
        user_id=test_user.id,
        entity_type="project",
        entity_id=project.id,
    )
    favorite2 = FavoriteModel(
        user_id=test_user.id,
        entity_type="space",
        entity_id=space.id,
    )
    db_session.add(favorite1)
    db_session.add(favorite2)
    await db_session.flush()

    # Login to get token
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

    # List favorites filtered by entity type
    list_response = await client.get(
        "/api/v1/users/me/favorites",
        params={"entity_type": "project"},
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 1
    assert len(data["favorites"]) == 1
    assert data["favorites"][0]["entity_type"] == "project"


@pytest.mark.asyncio
async def test_delete_favorite_success(client: AsyncClient, test_user, db_session):
    """Test successful favorite deletion."""
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

    # Create project
    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    # Create favorite
    favorite = FavoriteModel(
        user_id=test_user.id,
        entity_type="project",
        entity_id=project.id,
    )
    db_session.add(favorite)
    await db_session.flush()

    # Login to get token
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

    # Delete favorite
    delete_response = await client.delete(
        f"/api/v1/users/me/favorites/{favorite.id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    # Verify favorite is deleted (hard-deleted, so we can't refresh it)
    # Instead, verify it doesn't exist
    from sqlalchemy import select

    result = await db_session.execute(select(FavoriteModel).where(FavoriteModel.id == favorite.id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_favorite_not_found(client: AsyncClient, test_user):
    """Test favorite deletion with non-existent ID."""
    # Login to get token
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

    # Try to delete non-existent favorite
    delete_response = await client.delete(
        f"/api/v1/users/me/favorites/{uuid4()}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 404


@pytest.mark.asyncio
async def test_create_favorite_requires_auth(client: AsyncClient):
    """Test favorite creation requires authentication."""
    response = await client.post(
        "/api/v1/users/me/favorites",
        json={
            "entity_type": "project",
            "entity_id": str(uuid4()),
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_favorites_requires_auth(client: AsyncClient):
    """Test favorite listing requires authentication."""
    response = await client.get("/api/v1/users/me/favorites")
    assert response.status_code == 401
