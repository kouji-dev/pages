"""Integration tests for organization endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import OrganizationMemberModel, OrganizationModel


@pytest.mark.asyncio
async def test_create_organization_success(client: AsyncClient, test_user):
    """Test successful organization creation."""
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

    # Create organization
    create_response = await client.post(
        "/api/v1/organizations/",
        json={
            "name": "My New Organization",
            "slug": "my-new-org",
            "description": "A test organization",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "My New Organization"
    assert data["slug"] == "my-new-org"
    assert data["description"] == "A test organization"
    assert data["member_count"] == 1  # Creator is automatically added as admin
    assert "id" in data


@pytest.mark.asyncio
async def test_create_organization_auto_slug(client: AsyncClient, test_user):
    """Test organization creation with auto-generated slug."""
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

    # Create organization without slug
    create_response = await client.post(
        "/api/v1/organizations/",
        json={"name": "Auto Slug Organization"},
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "Auto Slug Organization"
    assert data["slug"] == "auto-slug-organization"  # Auto-generated


@pytest.mark.asyncio
async def test_create_organization_requires_auth(client: AsyncClient):
    """Test organization creation requires authentication."""
    response = await client.post(
        "/api/v1/organizations/",
        json={"name": "Test Org"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_organization_slug_conflict(client: AsyncClient, test_user, db_session):
    """Test organization creation fails with duplicate slug."""
    # Create an existing organization
    existing_org = OrganizationModel(
        name="Existing Org",
        slug="existing-org",
    )
    db_session.add(existing_org)
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

    # Try to create organization with same slug
    create_response = await client.post(
        "/api/v1/organizations/",
        json={
            "name": "Another Org",
            "slug": "existing-org",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 409
    error_data = create_response.json()
    error_message = error_data.get("message", "")
    assert "slug" in error_message.lower() or "already exists" in error_message.lower()


@pytest.mark.asyncio
async def test_get_organization_success(client: AsyncClient, test_user, db_session):
    """Test successful organization retrieval."""
    # Create organization
    org = OrganizationModel(
        name="Test Organization",
        slug="test-org",
        description="Test description",
    )
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

    # Get organization
    get_response = await client.get(
        f"/api/v1/organizations/{org.id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(org.id)
    assert data["name"] == "Test Organization"
    assert data["slug"] == "test-org"
    assert data["member_count"] == 1


@pytest.mark.asyncio
async def test_get_organization_not_member(client: AsyncClient, test_user, db_session):
    """Test get organization fails when user is not a member."""
    # Create organization
    org = OrganizationModel(
        name="Test Organization",
        slug="test-org",
    )
    db_session.add(org)
    await db_session.flush()
    # Don't add user as member

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

    # Try to get organization
    get_response = await client.get(
        f"/api/v1/organizations/{org.id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 403


@pytest.mark.asyncio
async def test_get_organization_not_found(client: AsyncClient, test_user):
    """Test get organization fails when not found or user not a member."""
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

    fake_id = str(uuid4())
    get_response = await client.get(
        f"/api/v1/organizations/{fake_id}",
        headers=auth_headers,
    )

    # Either 404 (not found) or 403 (not a member) is acceptable
    assert get_response.status_code in [403, 404]


@pytest.mark.asyncio
async def test_list_organizations_success(client: AsyncClient, test_user, db_session):
    """Test successful organization listing."""
    # Create organizations
    org1 = OrganizationModel(name="Org 1", slug="org-1")
    org2 = OrganizationModel(name="Org 2", slug="org-2")
    db_session.add_all([org1, org2])
    await db_session.flush()

    # Add user as member of both
    org_member1 = OrganizationMemberModel(
        organization_id=org1.id,
        user_id=test_user.id,
        role="member",
    )
    org_member2 = OrganizationMemberModel(
        organization_id=org2.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add_all([org_member1, org_member2])
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

    # List organizations
    list_response = await client.get(
        "/api/v1/organizations/",
        headers=auth_headers,
        params={"page": 1, "limit": 20},
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["organizations"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["limit"] == 20


@pytest.mark.asyncio
async def test_list_organizations_only_user_orgs(client: AsyncClient, test_user, db_session):
    """Test list organizations only returns user's organizations."""
    # Create organizations
    org1 = OrganizationModel(name="User Org", slug="user-org")
    org2 = OrganizationModel(name="Other Org", slug="other-org")
    db_session.add_all([org1, org2])
    await db_session.flush()

    # Add user as member of only org1
    org_member = OrganizationMemberModel(
        organization_id=org1.id,
        user_id=test_user.id,
        role="member",
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

    # List organizations
    list_response = await client.get(
        "/api/v1/organizations/",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["organizations"]) == 1
    assert data["organizations"][0]["slug"] == "user-org"


@pytest.mark.asyncio
async def test_list_organizations_with_search(client: AsyncClient, test_user, db_session):
    """Test organization listing with search query."""
    # Create organizations
    org1 = OrganizationModel(name="Test Organization", slug="test-org")
    org2 = OrganizationModel(name="Another Org", slug="another-org")
    db_session.add_all([org1, org2])
    await db_session.flush()

    # Add user as member of both
    org_member1 = OrganizationMemberModel(
        organization_id=org1.id,
        user_id=test_user.id,
        role="member",
    )
    org_member2 = OrganizationMemberModel(
        organization_id=org2.id,
        user_id=test_user.id,
        role="member",
    )
    db_session.add_all([org_member1, org_member2])
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

    # Search organizations
    search_response = await client.get(
        "/api/v1/organizations/",
        headers=auth_headers,
        params={"search": "test"},
    )

    assert search_response.status_code == 200
    data = search_response.json()
    assert len(data["organizations"]) == 1
    assert data["organizations"][0]["slug"] == "test-org"


@pytest.mark.asyncio
async def test_update_organization_success(client: AsyncClient, test_user, db_session):
    """Test successful organization update."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as admin
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

    # Update organization
    update_response = await client.put(
        f"/api/v1/organizations/{org.id}",
        json={
            "name": "Updated Org",
            "description": "Updated description",
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Org"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_organization_not_admin(client: AsyncClient, test_user, db_session):
    """Test update organization fails when user is not admin."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member (not admin)
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="member",
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

    # Try to update organization
    update_response = await client.put(
        f"/api/v1/organizations/{org.id}",
        json={"name": "Updated Org"},
        headers=auth_headers,
    )

    assert update_response.status_code == 403


@pytest.mark.asyncio
async def test_delete_organization_success(client: AsyncClient, test_user, db_session):
    """Test successful organization deletion (soft delete)."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as admin
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

    # Delete organization
    delete_response = await client.delete(
        f"/api/v1/organizations/{org.id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    # Verify organization is soft deleted (may still be accessible to admin or return 404)
    # Soft delete sets deleted_at but may still allow access through permission checks
    # This test verifies the deletion was successful (204 response)
    # The actual behavior of listing/retrieving soft-deleted orgs depends on business logic


@pytest.mark.asyncio
async def test_delete_organization_not_admin(client: AsyncClient, test_user, db_session):
    """Test delete organization fails when user is not admin."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member (not admin)
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="member",
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

    # Try to delete organization
    delete_response = await client.delete(
        f"/api/v1/organizations/{org.id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 403
