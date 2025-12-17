"""Integration tests for custom field endpoints."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    ProjectMemberModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_create_custom_field_success(client: AsyncClient, test_user, db_session):
    """Test successful custom field creation."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
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

    # Add user as project member
    project_member = ProjectMemberModel(
        project_id=project.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(project_member)
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

    # Create custom field
    create_response = await client.post(
        f"/api/v1/projects/{project.id}/custom-fields",
        json={
            "name": "Priority Level",
            "type": "select",
            "is_required": False,
            "options": ["Low", "Medium", "High"],
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "Priority Level"
    assert data["type"] == "select"
    assert data["options"] == ["Low", "Medium", "High"]
    assert "id" in data


@pytest.mark.asyncio
async def test_list_custom_fields_success(client: AsyncClient, test_user, db_session):
    """Test successfully listing custom fields."""
    # Setup same as above
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    project_member = ProjectMemberModel(
        project_id=project.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(project_member)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # List custom fields
    list_response = await client.get(
        f"/api/v1/projects/{project.id}/custom-fields",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert "fields" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_custom_field_success(client: AsyncClient, test_user, db_session):
    """Test successfully getting a custom field by ID."""
    # Setup
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    project_member = ProjectMemberModel(
        project_id=project.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(project_member)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create custom field
    create_response = await client.post(
        f"/api/v1/projects/{project.id}/custom-fields",
        json={
            "name": "Priority Level",
            "type": "select",
            "is_required": False,
            "options": ["Low", "Medium", "High"],
        },
        headers=auth_headers,
    )
    field_id = create_response.json()["id"]

    # Get custom field
    get_response = await client.get(
        f"/api/v1/custom-fields/{field_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == field_id
    assert data["name"] == "Priority Level"


@pytest.mark.asyncio
async def test_update_custom_field_success(client: AsyncClient, test_user, db_session):
    """Test successfully updating a custom field."""
    # Setup
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    project_member = ProjectMemberModel(
        project_id=project.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(project_member)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create custom field
    create_response = await client.post(
        f"/api/v1/projects/{project.id}/custom-fields",
        json={
            "name": "Priority Level",
            "type": "select",
            "is_required": False,
            "options": ["Low", "Medium", "High"],
        },
        headers=auth_headers,
    )
    field_id = create_response.json()["id"]

    # Update custom field
    update_response = await client.put(
        f"/api/v1/custom-fields/{field_id}",
        json={
            "name": "Updated Priority",
            "is_required": True,
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Priority"
    assert data["is_required"] is True


@pytest.mark.asyncio
async def test_delete_custom_field_success(client: AsyncClient, test_user, db_session):
    """Test successfully deleting a custom field."""
    # Setup
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    project_member = ProjectMemberModel(
        project_id=project.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(project_member)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create custom field
    create_response = await client.post(
        f"/api/v1/projects/{project.id}/custom-fields",
        json={
            "name": "Priority Level",
            "type": "select",
            "is_required": False,
            "options": ["Low", "Medium", "High"],
        },
        headers=auth_headers,
    )
    field_id = create_response.json()["id"]

    # Delete custom field
    delete_response = await client.delete(
        f"/api/v1/custom-fields/{field_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    # Verify custom field is deleted
    get_response = await client.get(
        f"/api/v1/custom-fields/{field_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404
