"""Integration tests for template endpoints."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    TemplateModel,
)


@pytest.mark.asyncio
async def test_create_template_success(client: AsyncClient, test_user, db_session):
    """Test successful template creation."""
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

    # Create template
    create_response = await client.post(
        "/api/v1/templates/",
        json={
            "organization_id": str(org.id),
            "name": "My New Template",
            "description": "A test template",
            "content": "# Template Content",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "My New Template"
    assert data["description"] == "A test template"
    assert data["content"] == "# Template Content"
    assert data["organization_id"] == str(org.id)
    assert "id" in data


@pytest.mark.asyncio
async def test_get_template_success(client: AsyncClient, test_user, db_session):
    """Test successful template retrieval."""
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

    # Create template
    template = TemplateModel(
        organization_id=org.id,
        name="Test Template",
        description="A test template",
        content="# Template Content",
        created_by=test_user.id,
    )
    db_session.add(template)
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

    # Get template
    get_response = await client.get(f"/api/v1/templates/{template.id}", headers=auth_headers)

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(template.id)
    assert data["name"] == "Test Template"
    assert data["content"] == "# Template Content"


@pytest.mark.asyncio
async def test_list_templates_success(client: AsyncClient, test_user, db_session):
    """Test successful template listing."""
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

    # Create templates
    template1 = TemplateModel(organization_id=org.id, name="Template 1", created_by=test_user.id)
    template2 = TemplateModel(organization_id=org.id, name="Template 2", created_by=test_user.id)
    db_session.add(template1)
    db_session.add(template2)
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

    # List templates
    list_response = await client.get(
        f"/api/v1/templates/?organization_id={org.id}", headers=auth_headers
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["templates"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_update_template_success(client: AsyncClient, test_user, db_session):
    """Test successful template update."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as admin member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Create template
    template = TemplateModel(
        organization_id=org.id,
        name="Test Template",
        description="Original description",
        content="# Original Content",
        created_by=test_user.id,
    )
    db_session.add(template)
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

    # Update template
    update_response = await client.put(
        f"/api/v1/templates/{template.id}",
        json={
            "name": "Updated Template",
            "description": "Updated description",
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Template"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_template_success(client: AsyncClient, test_user, db_session):
    """Test successful template deletion."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as admin member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Create template
    template = TemplateModel(organization_id=org.id, name="Test Template", created_by=test_user.id)
    db_session.add(template)
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

    # Delete template
    delete_response = await client.delete(f"/api/v1/templates/{template.id}", headers=auth_headers)

    assert delete_response.status_code == 204

    # Verify template is soft-deleted (should not appear in list)
    list_response = await client.get(
        f"/api/v1/templates/?organization_id={org.id}", headers=auth_headers
    )
    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 0
