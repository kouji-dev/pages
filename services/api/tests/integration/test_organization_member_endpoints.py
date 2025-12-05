"""Integration tests for organization member endpoints."""

import pytest
from httpx import AsyncClient
from uuid import uuid4

from src.infrastructure.database.models import OrganizationMemberModel, OrganizationModel


@pytest.mark.asyncio
async def test_add_member_success(client: AsyncClient, admin_user, test_user, db_session):
    """Test successful member addition."""
    # Create organization with unique slug
    org = OrganizationModel(
        name="Test Organization",
        slug=f"test-org-{uuid4().hex[:8]}",
    )
    db_session.add(org)
    await db_session.flush()

    # Add admin_user as admin
    admin_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=admin_user.id,
        role="admin",
    )
    db_session.add(admin_member)
    await db_session.flush()

    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {admin_token}"}

    # Add member
    add_response = await client.post(
        f"/api/v1/organizations/{org.id}/members",
        json={
            "user_id": str(test_user.id),
            "role": "member",
        },
        headers=auth_headers,
    )

    assert add_response.status_code == 201
    data = add_response.json()
    assert data["user_id"] == str(test_user.id)
    assert data["role"] == "member"
    assert data["user_name"] == test_user.name
    assert data["user_email"] == test_user.email.value


@pytest.mark.asyncio
async def test_add_member_requires_admin(client: AsyncClient, test_user, db_session):
    """Test adding member requires admin role."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
    db_session.add(org)
    await db_session.flush()

    # Add test_user as regular member (not admin)
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="member",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Login as regular member
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

    # Try to add member (should fail)
    another_user_id = str(uuid4())
    add_response = await client.post(
        f"/api/v1/organizations/{org.id}/members",
        json={"user_id": another_user_id, "role": "member"},
        headers=auth_headers,
    )

    assert add_response.status_code == 403


@pytest.mark.asyncio
async def test_add_member_already_member(
    client: AsyncClient, admin_user, test_user, db_session
):
    """Test adding member fails when user is already a member."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
    db_session.add(org)
    await db_session.flush()

    # Add both users as members
    admin_member = OrganizationMemberModel(
        organization_id=org.id, user_id=admin_user.id, role="admin"
    )
    test_member = OrganizationMemberModel(
        organization_id=org.id, user_id=test_user.id, role="member"
    )
    db_session.add_all([admin_member, test_member])
    await db_session.flush()

    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {admin_token}"}

    # Try to add test_user again
    add_response = await client.post(
        f"/api/v1/organizations/{org.id}/members",
        json={"user_id": str(test_user.id), "role": "member"},
        headers=auth_headers,
    )

    assert add_response.status_code == 409


@pytest.mark.asyncio
async def test_list_members_success(client: AsyncClient, admin_user, test_user, db_session):
    """Test successful member listing."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
    db_session.add(org)
    await db_session.flush()

    # Add members
    admin_member = OrganizationMemberModel(
        organization_id=org.id, user_id=admin_user.id, role="admin"
    )
    test_member = OrganizationMemberModel(
        organization_id=org.id, user_id=test_user.id, role="member"
    )
    db_session.add_all([admin_member, test_member])
    await db_session.flush()

    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {admin_token}"}

    # List members
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/members",
        headers=auth_headers,
        params={"page": 1, "limit": 20},
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["members"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_list_members_requires_member(client: AsyncClient, test_user, db_session):
    """Test listing members requires organization membership."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
    db_session.add(org)
    await db_session.flush()
    # Don't add test_user as member

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

    # Try to list members
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/members",
        headers=auth_headers,
    )

    assert list_response.status_code == 403


@pytest.mark.asyncio
async def test_update_member_role_success(
    client: AsyncClient, admin_user, test_user, db_session
):
    """Test successful member role update."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
    db_session.add(org)
    await db_session.flush()

    # Add members
    admin_member = OrganizationMemberModel(
        organization_id=org.id, user_id=admin_user.id, role="admin"
    )
    test_member = OrganizationMemberModel(
        organization_id=org.id, user_id=test_user.id, role="member"
    )
    db_session.add_all([admin_member, test_member])
    await db_session.flush()

    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {admin_token}"}

    # Update role
    update_response = await client.put(
        f"/api/v1/organizations/{org.id}/members/{test_user.id}",
        json={"role": "admin"},
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_update_role_prevent_remove_last_admin(
    client: AsyncClient, admin_user, db_session
):
    """Test update role prevents removing last admin."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
    db_session.add(org)
    await db_session.flush()

    # Add only one admin
    admin_member = OrganizationMemberModel(
        organization_id=org.id, user_id=admin_user.id, role="admin"
    )
    db_session.add(admin_member)
    await db_session.flush()

    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {admin_token}"}

    # Try to change own role from admin to member
    update_response = await client.put(
        f"/api/v1/organizations/{org.id}/members/{admin_user.id}",
        json={"role": "member"},
        headers=auth_headers,
    )

    assert update_response.status_code == 400
    assert "last admin" in update_response.json()["message"].lower()


@pytest.mark.asyncio
async def test_remove_member_success(
    client: AsyncClient, admin_user, test_user, db_session
):
    """Test successful member removal."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
    db_session.add(org)
    await db_session.flush()

    # Add members
    admin_member = OrganizationMemberModel(
        organization_id=org.id, user_id=admin_user.id, role="admin"
    )
    test_member = OrganizationMemberModel(
        organization_id=org.id, user_id=test_user.id, role="member"
    )
    db_session.add_all([admin_member, test_member])
    await db_session.flush()

    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {admin_token}"}

    # Remove member
    remove_response = await client.delete(
        f"/api/v1/organizations/{org.id}/members/{test_user.id}",
        headers=auth_headers,
    )

    assert remove_response.status_code == 204

    # Verify member is removed (can't list them)
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/members",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["members"]) == 1
    assert data["members"][0]["user_id"] == str(admin_user.id)


@pytest.mark.asyncio
async def test_remove_member_self(client: AsyncClient, test_user, db_session):
    """Test user can remove themselves from organization."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id, user_id=test_user.id, role="member"
    )
    db_session.add(org_member)
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

    # Remove self
    remove_response = await client.delete(
        f"/api/v1/organizations/{org.id}/members/{test_user.id}",
        headers=auth_headers,
    )

    assert remove_response.status_code == 204


@pytest.mark.asyncio
async def test_remove_member_prevent_remove_last_admin(
    client: AsyncClient, admin_user, db_session
):
    """Test remove member prevents removing last admin."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
    db_session.add(org)
    await db_session.flush()

    # Add only one admin
    admin_member = OrganizationMemberModel(
        organization_id=org.id, user_id=admin_user.id, role="admin"
    )
    db_session.add(admin_member)
    await db_session.flush()

    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email.value,
            "password": "AdminPassword123!",
        },
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {admin_token}"}

    # Try to remove self (last admin)
    remove_response = await client.delete(
        f"/api/v1/organizations/{org.id}/members/{admin_user.id}",
        headers=auth_headers,
    )

    assert remove_response.status_code == 400
    assert "last admin" in remove_response.json()["message"].lower()

