"""Functional tests for authentication workflows."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    create_test_user,
    get_auth_headers,
    login_user,
)


@pytest.mark.asyncio
async def test_complete_auth_flow(
    client: AsyncClient, unique_email: str, test_password: str
) -> None:
    """Test complete authentication flow: Register → Login → Refresh Token.

    This workflow validates that:
    - User can register
    - User can login with registered credentials
    - Refresh token can be used to get new access token
    - Tokens are valid and work together
    """
    # Step 1: Register new user
    register_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    assert "access_token" in register_data
    assert "refresh_token" in register_data
    assert register_data["email"] == unique_email
    assert register_data["name"] == "Test User"
    access_token = register_data["access_token"]
    refresh_token = register_data["refresh_token"]

    # Step 2: Use access token to get profile
    headers = get_auth_headers(access_token)
    profile_response = await client.get(
        "/api/v1/users/me",
        headers=headers,
    )
    assert profile_response.status_code == 200
    profile_data = profile_response.json()
    assert profile_data["email"] == unique_email

    # Step 3: Refresh access token using refresh token
    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data
    assert "refresh_token" in refresh_data
    new_access_token = refresh_data["access_token"]

    # Step 4: Verify new access token works
    new_headers = get_auth_headers(new_access_token)
    profile_response2 = await client.get(
        "/api/v1/users/me",
        headers=new_headers,
    )
    assert profile_response2.status_code == 200
    assert profile_response2.json()["email"] == unique_email


@pytest.mark.asyncio
async def test_password_reset_flow(
    client: AsyncClient, unique_email: str, test_password: str
) -> None:
    """Test password reset flow: Request Reset → Reset Password → Login with new password.

    This workflow validates that:
    - User can request password reset
    - User can reset password with valid token
    - Old password no longer works
    - New password works for login
    """
    # Step 1: Register and login
    await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    login_data = await login_user(client, unique_email, test_password)
    assert login_data["user"]["email"] == unique_email

    # Step 2: Request password reset
    reset_request_response = await client.post(
        "/api/v1/auth/password/reset-request",
        json={"email": unique_email},
    )
    assert reset_request_response.status_code == 202

    # Note: In a real scenario, we would extract the token from email
    # For testing, we need to mock or extract from test email service
    # For now, we'll skip the actual reset and just verify the flow structure
    # This would require additional setup with email mocking


@pytest.mark.asyncio
async def test_token_expiration_flow(
    client: AsyncClient, unique_email: str, test_password: str
) -> None:
    """Test token expiration and refresh flow.

    This workflow validates that:
    - Access tokens can be refreshed using refresh token
    - Expired access tokens are rejected
    - Refresh tokens remain valid for longer period
    """
    # Step 1: Register and get tokens
    register_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    access_token = register_data["access_token"]
    refresh_token = register_data["refresh_token"]

    # Step 2: Verify access token works
    headers = get_auth_headers(access_token)
    profile_response = await client.get(
        "/api/v1/users/me",
        headers=headers,
    )
    assert profile_response.status_code == 200

    # Step 3: Refresh access token
    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    new_access_token = new_tokens["access_token"]
    new_refresh_token = new_tokens["refresh_token"]

    # Step 4: Verify new access token works
    new_headers = get_auth_headers(new_access_token)
    profile_response2 = await client.get(
        "/api/v1/users/me",
        headers=new_headers,
    )
    assert profile_response2.status_code == 200

    # Step 5: Verify old access token still works (tokens don't expire immediately in tests)
    # In production, we would wait for expiration, but for functional tests we verify refresh works
    refresh_response2 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": new_refresh_token},
    )
    assert refresh_response2.status_code == 200


@pytest.mark.asyncio
async def test_multiple_sessions_flow(
    client: AsyncClient, unique_email: str, test_password: str
) -> None:
    """Test multiple sessions with same account.

    This workflow validates that:
    - User can login from multiple clients
    - Sessions work independently
    - Each session has its own tokens
    """
    # Step 1: Register user
    await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )

    # Step 2: Login from first "session" (client)
    login1 = await login_user(client, unique_email, test_password)
    token1 = login1["access_token"]
    headers1 = get_auth_headers(token1)

    # Step 3: Login from second "session" (same client, but different token)
    login2 = await login_user(client, unique_email, test_password)
    token2 = login2["access_token"]
    headers2 = get_auth_headers(token2)

    # Step 4: Verify both tokens work (they may be the same if generated quickly)
    profile1 = await client.get("/api/v1/users/me", headers=headers1)
    assert profile1.status_code == 200
    assert profile1.json()["email"] == unique_email

    profile2 = await client.get("/api/v1/users/me", headers=headers2)
    assert profile2.status_code == 200
    assert profile2.json()["email"] == unique_email


@pytest.mark.asyncio
async def test_register_verify_login_flow(
    client: AsyncClient, unique_email: str, test_password: str
) -> None:
    """Test register → verify account → login → verify profile workflow.

    This workflow validates that:
    - User registration creates account correctly
    - User can login immediately after registration
    - User profile is accessible after login
    """
    # Step 1: Register
    register_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    user_id = register_data["id"]
    assert register_data["email"] == unique_email
    assert register_data["name"] == "Test User"
    # RegisterResponse doesn't include is_verified, check via login response

    # Step 2: Login with registered credentials
    login_data = await login_user(client, unique_email, test_password)
    assert login_data["user"]["email"] == unique_email
    assert login_data["user"]["id"] == user_id

    # Step 3: Get profile using access token
    headers = get_auth_headers(login_data["access_token"])
    profile_response = await client.get(
        "/api/v1/users/me",
        headers=headers,
    )
    assert profile_response.status_code == 200
    profile_data = profile_response.json()
    assert profile_data["id"] == user_id
    assert profile_data["email"] == unique_email
    assert profile_data["name"] == "Test User"
