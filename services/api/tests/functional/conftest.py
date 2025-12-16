"""Fixtures and helpers for functional tests (E2E API workflows)."""

from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient


def get_auth_headers(token: str) -> dict[str, str]:
    """Get authentication headers with Bearer token.

    Args:
        token: JWT access token

    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {token}"}


async def create_test_user(
    client: AsyncClient,
    email: str,
    password: str,
    name: str,
) -> dict[str, Any]:
    """Create a test user via registration endpoint.

    Args:
        client: HTTP client
        email: User email
        password: User password
        name: User name

    Returns:
        User data with tokens
    """
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "name": name,
        },
    )
    assert response.status_code == 201
    return response.json()


async def login_user(
    client: AsyncClient,
    email: str,
    password: str,
) -> dict[str, Any]:
    """Login a user and get tokens.

    Args:
        client: HTTP client
        email: User email
        password: User password

    Returns:
        Login response with tokens and user data
    """
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 200
    return response.json()


async def authenticated_client(
    client: AsyncClient,
    user_data: dict[str, Any] | None = None,
    email: str | None = None,
    password: str | None = None,
) -> tuple[AsyncClient, dict[str, str], dict[str, Any]]:
    """Create an authenticated client with valid token.

    Args:
        client: HTTP client
        user_data: User data from registration (must contain access_token)
        email: User email for login (if user_data not provided)
        password: User password for login (if user_data not provided)

    Returns:
        Tuple of (client, auth_headers, user_data)
    """
    if user_data and "access_token" in user_data:
        token = user_data["access_token"]
        user_info = user_data
    elif email and password:
        login_data = await login_user(client, email, password)
        token = login_data["access_token"]
        user_info = login_data
    else:
        raise ValueError("Either user_data with access_token or email/password must be provided")

    headers = get_auth_headers(token)
    return client, headers, user_info


async def create_test_organization(
    client: AsyncClient,
    headers: dict[str, str],
    name: str,
    slug: str | None = None,
) -> dict[str, Any]:
    """Create a test organization.

    Args:
        client: HTTP client
        headers: Authentication headers
        name: Organization name
        slug: Organization slug (auto-generated if not provided)

    Returns:
        Organization data
    """
    payload: dict[str, Any] = {"name": name}
    if slug:
        payload["slug"] = slug

    response = await client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


async def create_test_project(
    client: AsyncClient,
    headers: dict[str, str],
    organization_id: str,
    name: str,
    key: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a test project.

    Args:
        client: HTTP client
        headers: Authentication headers
        organization_id: Organization UUID
        name: Project name
        key: Project key (auto-generated if not provided)
        description: Project description

    Returns:
        Project data
    """
    payload: dict[str, Any] = {
        "organization_id": organization_id,
        "name": name,
    }
    if key:
        payload["key"] = key
    if description:
        payload["description"] = description

    response = await client.post(
        "/api/v1/projects/",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


async def create_test_space(
    client: AsyncClient,
    headers: dict[str, str],
    organization_id: str,
    name: str,
    key: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a test space.

    Args:
        client: HTTP client
        headers: Authentication headers
        organization_id: Organization UUID
        name: Space name
        key: Space key (auto-generated if not provided)
        description: Space description

    Returns:
        Space data
    """
    payload: dict[str, Any] = {
        "organization_id": organization_id,
        "name": name,
    }
    if key:
        payload["key"] = key
    if description:
        payload["description"] = description

    response = await client.post(
        "/api/v1/spaces/",
        json=payload,
        headers=headers,
    )
    if response.status_code != 201:
        # Print error details for debugging
        try:
            error_data = response.json()
        except Exception:
            error_data = response.text
        raise AssertionError(f"Expected 201, got {response.status_code}. Error: {error_data}")
    return response.json()


async def create_test_issue(
    client: AsyncClient,
    headers: dict[str, str],
    project_id: str,
    title: str,
    description: str | None = None,
    issue_type: str = "task",
    status: str = "todo",
    priority: str = "medium",
    story_points: int | None = None,
) -> dict[str, Any]:
    """Create a test issue.

    Args:
        client: HTTP client
        headers: Authentication headers
        project_id: Project UUID
        title: Issue title
        description: Issue description
        issue_type: Issue type (bug, task, story, epic)
        status: Issue status (todo, in_progress, done, etc.)
        priority: Issue priority (low, medium, high, critical)
        story_points: Story points estimation

    Returns:
        Issue data
    """
    payload: dict[str, Any] = {
        "project_id": project_id,
        "title": title,
        "type": issue_type,
        "status": status,
        "priority": priority,
    }
    if description:
        payload["description"] = description
    if story_points is not None:
        payload["story_points"] = story_points

    response = await client.post(
        "/api/v1/issues/",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


async def create_test_page(
    client: AsyncClient,
    headers: dict[str, str],
    space_id: str,
    title: str,
    content: str = "",
    parent_id: str | None = None,
) -> dict[str, Any]:
    """Create a test page.

    Args:
        client: HTTP client
        headers: Authentication headers
        space_id: Space UUID
        title: Page title
        content: Page content
        parent_id: Parent page UUID (for hierarchy)

    Returns:
        Page data
    """
    payload: dict[str, Any] = {
        "space_id": space_id,
        "title": title,
        "content": content,
    }
    if parent_id:
        payload["parent_id"] = parent_id

    response = await client.post(
        "/api/v1/pages/",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


async def create_test_template(
    client: AsyncClient,
    headers: dict[str, str],
    organization_id: str,
    name: str,
    content: str = "",
    description: str | None = None,
    is_default: bool = False,
) -> dict[str, Any]:
    """Create a test template.

    Args:
        client: HTTP client
        headers: Authentication headers
        organization_id: Organization UUID
        name: Template name
        content: Template content
        description: Template description
        is_default: Whether template is default

    Returns:
        Template data
    """
    payload: dict[str, Any] = {
        "organization_id": organization_id,
        "name": name,
        "content": content,
        "is_default": is_default,
    }
    if description:
        payload["description"] = description

    response = await client.post(
        "/api/v1/templates/",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def get_user_id(user_data: dict[str, Any]) -> str:
    """Get user ID from user data (handles both RegisterResponse and LoginResponse).

    Args:
        user_data: User data from registration or login

    Returns:
        User ID as string
    """
    # LoginResponse has "user" with "id"
    if "user" in user_data and isinstance(user_data["user"], dict) and "id" in user_data["user"]:
        return str(user_data["user"]["id"])
    # RegisterResponse has "id" directly
    if "id" in user_data:
        return str(user_data["id"])
    # Fallback: try direct "id"
    return str(user_data.get("id", ""))


@pytest.fixture
def unique_email() -> str:
    """Generate a unique email for testing.

    Returns:
        Unique email address
    """
    return f"test-{uuid4().hex[:8]}@example.com"


@pytest.fixture
def test_password() -> str:
    """Get standard test password.

    Returns:
        Test password
    """
    return "TestPassword123!"
