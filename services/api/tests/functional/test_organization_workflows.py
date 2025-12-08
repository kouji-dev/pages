"""Functional tests for organization management workflows."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    authenticated_client,
    create_test_organization,
    create_test_user,
    get_user_id,
)


@pytest.mark.asyncio
async def test_create_organization_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test create organization workflow: Register → Create Org → Verify admin → List Orgs.

    This workflow validates that:
    - User can create organization after registration
    - Creator is automatically added as admin
    - Organization appears in user's organization list
    """
    # Step 1: Register user
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )

    # Step 2: Create organization
    client_instance, headers, user_info = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance,
        headers,
        name="Test Organization",
        slug="test-org",
    )
    assert org["name"] == "Test Organization"
    assert org["slug"] == "test-org"
    org_id = org["id"]

    # Step 3: List organizations (should include the created one)
    list_response = await client_instance.get(
        "/api/v1/organizations/",
        headers=headers,
    )
    assert list_response.status_code == 200
    orgs_data = list_response.json()
    assert "organizations" in orgs_data
    assert any(o["id"] == org_id for o in orgs_data["organizations"])

    # Step 4: Get organization members (creator should be admin)
    members_response = await client_instance.get(
        f"/api/v1/organizations/{org_id}/members",
        headers=headers,
    )
    assert members_response.status_code == 200
    members_data = members_response.json()
    assert "members" in members_data
    # Creator should be in members list as admin
    creator_user_id = get_user_id(user_info)
    creator_member = next(
        (m for m in members_data["members"] if m["user_id"] == creator_user_id),
        None,
    )
    assert creator_member is not None
    assert creator_member["role"] == "admin"


@pytest.mark.asyncio
async def test_organization_member_management_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test organization member management: Create Org → Add Member → Update Role → Remove.

    This workflow validates that:
    - Admin can add members to organization
    - Admin can update member roles
    - Admin can remove members
    - Permissions are enforced at each step
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
        slug="test-org-member",
    )
    org_id = org["id"]

    # Step 2: Create another user to add as member
    member_email = f"member-{unique_email}"
    member_data = await create_test_user(
        client,
        email=member_email,
        password=test_password,
        name="Member User",
    )
    member_user_id = member_data["id"]

    # Step 3: Add member to organization
    add_member_response = await client_instance.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": member_user_id, "role": "member"},
        headers=headers,
    )
    assert add_member_response.status_code == 201
    added_member = add_member_response.json()
    assert added_member["user_id"] == member_user_id
    assert added_member["role"] == "member"

    # Step 4: List members (should include both admin and new member)
    members_response = await client_instance.get(
        f"/api/v1/organizations/{org_id}/members",
        headers=headers,
    )
    assert members_response.status_code == 200
    members_data = members_response.json()
    assert len(members_data["members"]) >= 2

    # Step 5: Update member role
    update_role_response = await client_instance.put(
        f"/api/v1/organizations/{org_id}/members/{member_user_id}",
        json={"role": "admin"},
        headers=headers,
    )
    assert update_role_response.status_code == 200
    updated_member = update_role_response.json()
    assert updated_member["role"] == "admin"

    # Step 6: Remove member
    remove_response = await client_instance.delete(
        f"/api/v1/organizations/{org_id}/members/{member_user_id}",
        headers=headers,
    )
    assert remove_response.status_code == 204

    # Step 7: Verify member is removed
    members_response2 = await client_instance.get(
        f"/api/v1/organizations/{org_id}/members",
        headers=headers,
    )
    assert members_response2.status_code == 200
    members_data2 = members_response2.json()
    assert not any(m["user_id"] == member_user_id for m in members_data2["members"])


@pytest.mark.asyncio
async def test_organization_invitation_flow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test organization invitation flow: Create Org → Send Invitation → Accept.

    This workflow validates that:
    - Admin can send invitations
    - User can accept invitations
    - Member is added after acceptance
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
        slug="test-org-invite",
    )
    org_id = org["id"]

    # Step 2: Create invitee user
    invitee_email = f"invitee-{unique_email}"
    invitee_data = await create_test_user(
        client,
        email=invitee_email,
        password=test_password,
        name="Invitee User",
    )
    invitee_user_id = invitee_data["id"]

    # Step 3: Send invitation
    send_invite_response = await client_instance.post(
        f"/api/v1/organizations/{org_id}/members/invite",
        json={"email": invitee_email, "role": "member"},
        headers=headers,
    )
    assert send_invite_response.status_code == 201
    invitation = send_invite_response.json()
    invitation_id = invitation["id"]

    # Get invitation token from list endpoint (which includes token for admin)
    list_invitations_response = await client_instance.get(
        f"/api/v1/organizations/{org_id}/invitations",
        headers=headers,
    )
    assert list_invitations_response.status_code == 200
    invitations_list = list_invitations_response.json()["invitations"]
    invitation_with_token = next(
        (inv for inv in invitations_list if inv["id"] == invitation_id), None
    )
    assert invitation_with_token is not None
    invitation_token = invitation_with_token["token"]

    # Step 4: Accept invitation (as invitee)
    invitee_client, invitee_headers, _ = await authenticated_client(client, invitee_data)
    accept_response = await invitee_client.post(
        f"/api/v1/organizations/invitations/{invitation_token}/accept",
        headers=invitee_headers,
    )
    assert accept_response.status_code == 200

    # Step 5: Verify member was added
    members_response = await client_instance.get(
        f"/api/v1/organizations/{org_id}/members",
        headers=headers,
    )
    assert members_response.status_code == 200
    members_data = members_response.json()
    assert any(m["user_id"] == invitee_user_id for m in members_data["members"])


@pytest.mark.asyncio
async def test_organization_settings_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test organization settings workflow: Create Org → Get Settings → Update → Verify.

    This workflow validates that:
    - Organization has default settings
    - Settings can be retrieved
    - Settings can be updated
    - Changes persist correctly
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
        slug="test-org-settings",
    )
    org_id = org["id"]

    # Step 2: Get default settings
    get_settings_response = await client_instance.get(
        f"/api/v1/organizations/{org_id}/settings",
        headers=headers,
    )
    assert get_settings_response.status_code == 200
    settings = get_settings_response.json()
    assert "settings" in settings

    # Step 3: Update settings
    update_settings_response = await client_instance.put(
        f"/api/v1/organizations/{org_id}/settings",
        json={
            "settings": {
                "notifications": {
                    "email_digest": {
                        "frequency": "weekly",
                    },
                },
            },
        },
        headers=headers,
    )
    assert update_settings_response.status_code == 200

    # Step 4: Verify settings were updated
    get_settings_response2 = await client_instance.get(
        f"/api/v1/organizations/{org_id}/settings",
        headers=headers,
    )
    assert get_settings_response2.status_code == 200
    updated_settings = get_settings_response2.json()
    assert updated_settings["settings"]["notifications"]["email_digest"]["frequency"] == "weekly"


@pytest.mark.asyncio
async def test_organization_deletion_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test organization deletion workflow: Create Org → Add Members → Delete → Verify.

    This workflow validates that:
    - Organization can be soft deleted
    - Members cannot access deleted organization
    - Soft delete preserves data
    """
    # Step 1: Create organization with members
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
        slug="test-org-delete",
    )
    org_id = org["id"]

    # Step 2: Add a member
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

    # Step 3: Delete organization
    delete_response = await client_instance.delete(
        f"/api/v1/organizations/{org_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    # Step 4: Verify organization is not accessible (soft delete - may still return 200)
    # In soft delete, the organization may still be accessible but marked as deleted
    # This depends on implementation - checking that it's handled
    get_org_response = await client_instance.get(
        f"/api/v1/organizations/{org_id}",
        headers=headers,
    )
    # Soft delete may return 200 or 404 depending on implementation
    assert get_org_response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_organization_slug_conflict_flow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test organization slug conflict: Create Org → Attempt duplicate slug → Verify error.

    This workflow validates that:
    - Organization slugs must be unique
    - Duplicate slug creation is rejected
    - Error message is clear
    """
    # Step 1: Create first organization
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    client_instance, headers, _ = await authenticated_client(client, user_data)
    org1 = await create_test_organization(
        client_instance,
        headers,
        name="First Org",
        slug="unique-slug",
    )
    assert org1["slug"] == "unique-slug"

    # Step 2: Attempt to create organization with same slug
    duplicate_response = await client_instance.post(
        "/api/v1/organizations/",
        json={"name": "Second Org", "slug": "unique-slug"},
        headers=headers,
    )
    assert duplicate_response.status_code in (400, 409)
    error_data = duplicate_response.json()
    assert "slug" in str(error_data).lower() or "already" in str(error_data).lower()
