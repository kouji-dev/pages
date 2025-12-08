"""Functional tests for user management workflows."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    authenticated_client,
    create_test_organization,
    create_test_user,
    get_user_id,
    login_user,
)


@pytest.mark.asyncio
async def test_user_profile_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test user profile workflow: Register → Get Profile → Update Name → Update Email → Update Password.

    This workflow validates that:
    - User profile can be retrieved
    - User name can be updated
    - User email can be updated (with password verification)
    - User password can be updated
    - Changes persist correctly
    """
    # Step 1: Register user
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    client_instance, headers, user_info = await authenticated_client(client, user_data)

    # Step 2: Get profile
    profile_response = await client_instance.get(
        "/api/v1/users/me",
        headers=headers,
    )
    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["name"] == "Test User"
    assert profile["email"] == unique_email

    # Step 3: Update name
    update_name_response = await client_instance.put(
        "/api/v1/users/me",
        json={"name": "Updated Name"},
        headers=headers,
    )
    assert update_name_response.status_code == 200
    updated_profile = update_name_response.json()
    assert updated_profile["name"] == "Updated Name"

    # Step 4: Update email (requires password verification)
    new_email = f"new-{unique_email}"
    update_email_response = await client_instance.put(
        "/api/v1/users/me/email",
        json={"new_email": new_email, "current_password": test_password},
        headers=headers,
    )
    assert update_email_response.status_code == 200

    # Step 5: Verify email was updated (login with new email)
    login_data = await login_user(client, new_email, test_password)
    assert login_data["user"]["email"] == new_email

    # Step 6: Update password
    new_password = "NewPassword123!"
    update_password_response = await client_instance.put(
        "/api/v1/users/me/password",
        json={
            "current_password": test_password,
            "new_password": new_password,
        },
        headers=headers,
    )
    assert update_password_response.status_code == 204  # No Content

    # Step 7: Verify new password works (old password should not)
    new_login_data = await login_user(client, new_email, new_password)
    assert new_login_data["user"]["email"] == new_email

    # Old password should not work
    old_login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": new_email, "password": test_password},
    )
    assert old_login_response.status_code == 401


@pytest.mark.asyncio
async def test_user_preferences_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test user preferences workflow: Register → Get Preferences → Update Theme → Update Language.

    This workflow validates that:
    - User preferences can be retrieved
    - Theme can be updated
    - Language can be updated
    - Notification preferences can be updated
    - Changes persist correctly
    """
    # Step 1: Register user
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    client_instance, headers, _ = await authenticated_client(client, user_data)

    # Step 2: Get default preferences
    get_prefs_response = await client_instance.get(
        "/api/v1/users/me/preferences",
        headers=headers,
    )
    assert get_prefs_response.status_code == 200
    prefs = get_prefs_response.json()
    assert "theme" in prefs
    assert "language" in prefs

    # Step 3: Update theme
    update_theme_response = await client_instance.put(
        "/api/v1/users/me/preferences",
        json={"theme": "dark"},
        headers=headers,
    )
    assert update_theme_response.status_code == 200
    updated_prefs = update_theme_response.json()
    assert updated_prefs["theme"] == "dark"

    # Step 4: Update language
    update_lang_response = await client_instance.put(
        "/api/v1/users/me/preferences",
        json={"language": "fr"},
        headers=headers,
    )
    assert update_lang_response.status_code == 200
    updated_prefs2 = update_lang_response.json()
    assert updated_prefs2["language"] == "fr"
    # Theme should still be dark (partial update)
    assert updated_prefs2["theme"] == "dark"

    # Step 5: Update notifications
    update_notif_response = await client_instance.put(
        "/api/v1/users/me/preferences",
        json={
            "notifications": {
                "email": {
                    "enabled": True,
                },
                "in_app": {
                    "enabled": False,
                },
            },
        },
        headers=headers,
    )
    assert update_notif_response.status_code == 200
    updated_prefs3 = update_notif_response.json()
    assert updated_prefs3["notifications"]["email"]["enabled"] is True
    assert updated_prefs3["notifications"]["in_app"]["enabled"] is False


@pytest.mark.asyncio
async def test_user_deactivation_flow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test user deactivation flow: Register → Login → Deactivate → Login fails → Reactivate → Login works.

    This workflow validates that:
    - User can be deactivated
    - Deactivated user cannot login
    - Admin can reactivate user
    - Reactivated user can login again
    """
    # Step 1: Register and login
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    client_instance, headers, user_info = await authenticated_client(client, user_data)

    # Step 2: Deactivate user
    deactivate_response = await client_instance.post(
        "/api/v1/users/me/deactivate",
        headers=headers,
    )
    assert deactivate_response.status_code == 204

    # Step 3: Attempt login (should fail)
    login_attempt = await client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": test_password},
    )
    assert login_attempt.status_code == 401

    # Step 4: Admin reactivates user
    # Create admin user and organization (admin must be admin of at least one org)

    admin_email = f"admin-{unique_email}"
    admin_data = await create_test_user(
        client,
        email=admin_email,
        password=test_password,
        name="Admin User",
    )
    admin_client, admin_headers, _ = await authenticated_client(client, admin_data)
    # Create organization so admin is admin of at least one org
    await create_test_organization(
        admin_client,
        admin_headers,
        name="Admin Org",
        slug="admin-org",
    )

    user_id = get_user_id(user_info)
    reactivate_response = await admin_client.post(
        f"/api/v1/users/{user_id}/reactivate",
        headers=admin_headers,
    )
    assert reactivate_response.status_code == 204

    # Step 5: Verify user can login again
    login_success = await login_user(client, unique_email, test_password)
    assert login_success["user"]["email"] == unique_email


@pytest.mark.asyncio
async def test_user_avatar_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test user avatar workflow: Register → Upload Avatar → Get Profile → Delete Avatar.

    This workflow validates that:
    - Avatar can be uploaded
    - Avatar URL is returned in profile
    - Avatar can be deleted
    - Profile reflects avatar changes
    """
    # Step 1: Register user
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    client_instance, headers, _ = await authenticated_client(client, user_data)

    # Step 2: Upload avatar
    # Create a simple test image (1x1 PNG) using PIL
    import io

    try:
        from PIL import Image

        # Create a simple colored image
        img = Image.new("RGB", (200, 200), color=(73, 109, 137))
        output = io.BytesIO()
        img.save(output, format="PNG")
        output.seek(0)
        png_data = output.read()
    except ImportError:
        # Fallback: Use a valid minimal PNG if PIL is not available
        # This is a valid 1x1 PNG image
        png_data = bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
            "890000000a49444154789c63000100000500010d0a2db40000000049454e44ae"
            "426082"
        )

    files = {"file": ("avatar.png", io.BytesIO(png_data), "image/png")}
    upload_response = await client_instance.post(
        "/api/v1/users/me/avatar",
        files=files,
        headers=headers,
    )
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    assert "avatar_url" in upload_data
    avatar_url = upload_data["avatar_url"]
    assert avatar_url is not None

    # Step 3: Get profile (should include avatar_url)
    profile_response = await client_instance.get(
        "/api/v1/users/me",
        headers=headers,
    )
    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["avatar_url"] == avatar_url

    # Step 4: Delete avatar
    delete_response = await client_instance.delete(
        "/api/v1/users/me/avatar",
        headers=headers,
    )
    assert delete_response.status_code == 200

    # Step 5: Verify avatar is removed from profile
    profile_response2 = await client_instance.get(
        "/api/v1/users/me",
        headers=headers,
    )
    assert profile_response2.status_code == 200
    profile2 = profile_response2.json()
    assert profile2["avatar_url"] is None
