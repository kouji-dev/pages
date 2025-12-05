"""Integration tests for invitation endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    InvitationModel,
    OrganizationMemberModel,
    OrganizationModel,
)


@pytest.mark.asyncio
async def test_send_invitation_success(client: AsyncClient, admin_user, db_session):
    """Test successful invitation sending."""
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

    # Send invitation
    invite_response = await client.post(
        f"/api/v1/organizations/{org.id}/members/invite",
        json={
            "email": "invited@example.com",
            "role": "member",
        },
        headers=auth_headers,
    )

    assert invite_response.status_code == 201
    data = invite_response.json()
    assert data["email"] == "invited@example.com"
    assert data["role"] == "member"
    assert data["organization_id"] == str(org.id)
    assert data["invited_by"] == str(admin_user.id)
    assert "token" not in data  # Token should not be in response for security
    assert data["accepted_at"] is None


@pytest.mark.asyncio
async def test_send_invitation_requires_admin(client: AsyncClient, test_user, db_session):
    """Test sending invitation requires admin role."""
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

    # Try to send invitation (should fail)
    invite_response = await client.post(
        f"/api/v1/organizations/{org.id}/members/invite",
        json={"email": "invited@example.com", "role": "member"},
        headers=auth_headers,
    )

    assert invite_response.status_code == 403


@pytest.mark.asyncio
async def test_send_invitation_already_member(
    client: AsyncClient, admin_user, test_user, db_session
):
    """Test sending invitation when user is already a member."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
    db_session.add(org)
    await db_session.flush()

    # Add admin_user as admin
    admin_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=admin_user.id,
        role="admin",
    )
    db_session.add(admin_member)

    # Add test_user as member
    member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="member",
    )
    db_session.add(member)
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

    # Try to send invitation to existing member (should fail)
    invite_response = await client.post(
        f"/api/v1/organizations/{org.id}/members/invite",
        json={"email": test_user.email.value, "role": "member"},
        headers=auth_headers,
    )

    assert invite_response.status_code == 409
    assert "already a member" in invite_response.json()["message"].lower()


@pytest.mark.asyncio
async def test_send_invitation_pending_exists(client: AsyncClient, admin_user, db_session):
    """Test sending invitation when pending invitation already exists."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
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

    # Create existing invitation
    from datetime import UTC, datetime, timedelta

    existing_invitation = InvitationModel(
        organization_id=org.id,
        email="invited@example.com",
        token="existing-token",
        role="member",
        invited_by=admin_user.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    db_session.add(existing_invitation)
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

    # Try to send duplicate invitation (should fail)
    invite_response = await client.post(
        f"/api/v1/organizations/{org.id}/members/invite",
        json={"email": "invited@example.com", "role": "member"},
        headers=auth_headers,
    )

    assert invite_response.status_code == 409
    assert "pending invitation" in invite_response.json()["message"].lower()


@pytest.mark.asyncio
async def test_accept_invitation_success(client: AsyncClient, test_user, admin_user, db_session):
    """Test successful invitation acceptance."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
    db_session.add(org)
    await db_session.flush()

    # Create invitation
    from datetime import UTC, datetime, timedelta

    invitation = InvitationModel(
        organization_id=org.id,
        email=test_user.email.value,
        token="test-invitation-token",
        role="member",
        invited_by=admin_user.id,  # Use existing admin user
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    db_session.add(invitation)
    await db_session.flush()

    # Login as invited user
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

    # Accept invitation
    accept_response = await client.post(
        f"/api/v1/organizations/invitations/{invitation.token}/accept",
        headers=auth_headers,
    )

    assert accept_response.status_code == 200
    data = accept_response.json()
    assert data["organization_id"] == str(org.id)
    assert data["organization_name"] == org.name
    assert data["role"] == "member"

    # Verify user was added as member
    from sqlalchemy import select

    result = await db_session.execute(
        select(OrganizationMemberModel).where(
            OrganizationMemberModel.organization_id == org.id,
            OrganizationMemberModel.user_id == test_user.id,
        )
    )
    member = result.scalar_one_or_none()
    assert member is not None
    assert member.role == "member"


@pytest.mark.asyncio
async def test_accept_invitation_email_mismatch(
    client: AsyncClient, test_user, admin_user, db_session
):
    """Test accepting invitation with email mismatch."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
    db_session.add(org)
    await db_session.flush()

    # Create invitation for different email
    from datetime import UTC, datetime, timedelta

    invitation = InvitationModel(
        organization_id=org.id,
        email="different@example.com",  # Different email
        token="test-invitation-token",
        role="member",
        invited_by=admin_user.id,  # Use existing admin user
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    db_session.add(invitation)
    await db_session.flush()

    # Login as test_user (different email)
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

    # Try to accept invitation (should fail)
    accept_response = await client.post(
        f"/api/v1/organizations/invitations/{invitation.token}/accept",
        headers=auth_headers,
    )

    assert accept_response.status_code == 400
    assert "email" in accept_response.json()["message"].lower()


@pytest.mark.asyncio
async def test_accept_invitation_expired(client: AsyncClient, test_user, admin_user, db_session):
    """Test accepting expired invitation."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
    db_session.add(org)
    await db_session.flush()

    # Create invitation with valid expiration first
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import text

    invitation = InvitationModel(
        organization_id=org.id,
        email=test_user.email.value,
        token="expired-token",
        role="member",
        invited_by=admin_user.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),  # Valid initially
    )
    db_session.add(invitation)
    await db_session.flush()

    # Manually set expired date in database using SQL (bypasses validation)
    expired_date = datetime.now(UTC) - timedelta(days=1)
    await db_session.execute(
        text("UPDATE invitations SET expires_at = :expires_at WHERE id = :id"),
        {"expires_at": expired_date, "id": invitation.id},
    )
    await db_session.commit()
    await db_session.refresh(invitation)

    # Login as invited user
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

    # Try to accept expired invitation (should fail)
    accept_response = await client.post(
        f"/api/v1/organizations/invitations/{invitation.token}/accept",
        headers=auth_headers,
    )

    assert accept_response.status_code == 400
    assert "expired" in accept_response.json()["message"].lower()


@pytest.mark.asyncio
async def test_list_invitations_success(client: AsyncClient, admin_user, db_session):
    """Test successfully listing invitations."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
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

    # Create invitations
    from datetime import UTC, datetime, timedelta

    invitation1 = InvitationModel(
        organization_id=org.id,
        email="invited1@example.com",
        token="token1",
        role="member",
        invited_by=admin_user.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    invitation2 = InvitationModel(
        organization_id=org.id,
        email="invited2@example.com",
        token="token2",
        role="admin",
        invited_by=admin_user.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    db_session.add(invitation1)
    db_session.add(invitation2)
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

    # List invitations
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/invitations",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["invitations"]) >= 2
    assert data["page"] == 1
    assert data["limit"] == 20


@pytest.mark.asyncio
async def test_list_invitations_requires_admin(client: AsyncClient, test_user, db_session):
    """Test listing invitations requires admin role."""
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

    # Try to list invitations (should fail)
    list_response = await client.get(
        f"/api/v1/organizations/{org.id}/invitations",
        headers=auth_headers,
    )

    assert list_response.status_code == 403


@pytest.mark.asyncio
async def test_cancel_invitation_success(client: AsyncClient, admin_user, db_session):
    """Test successfully canceling an invitation."""
    # Create organization with unique slug
    org = OrganizationModel(name="Test Organization", slug=f"test-org-{uuid4().hex[:8]}")
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

    # Create invitation
    from datetime import UTC, datetime, timedelta

    invitation = InvitationModel(
        organization_id=org.id,
        email="invited@example.com",
        token="cancel-me-token",
        role="member",
        invited_by=admin_user.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    db_session.add(invitation)
    await db_session.flush()
    invitation_id = invitation.id

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

    # Cancel invitation
    cancel_response = await client.delete(
        f"/api/v1/organizations/invitations/{invitation_id}",
        headers=auth_headers,
    )

    assert cancel_response.status_code == 204

    # Verify invitation was deleted
    from sqlalchemy import select

    result = await db_session.execute(
        select(InvitationModel).where(InvitationModel.id == invitation_id)
    )
    deleted_invitation = result.scalar_one_or_none()
    assert deleted_invitation is None


@pytest.mark.asyncio
async def test_cancel_invitation_requires_admin(
    client: AsyncClient, test_user, admin_user, db_session
):
    """Test canceling invitation requires admin role."""
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

    # Create invitation
    from datetime import UTC, datetime, timedelta

    invitation = InvitationModel(
        organization_id=org.id,
        email="invited@example.com",
        token="some-token",
        role="member",
        invited_by=admin_user.id,  # Use existing admin user
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    db_session.add(invitation)
    await db_session.flush()
    invitation_id = invitation.id

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

    # Try to cancel invitation (should fail)
    cancel_response = await client.delete(
        f"/api/v1/organizations/invitations/{invitation_id}",
        headers=auth_headers,
    )

    assert cancel_response.status_code == 403
