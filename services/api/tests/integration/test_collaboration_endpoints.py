"""Integration tests for collaboration endpoints."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    PageModel,
    SpaceModel,
)


@pytest.mark.asyncio
async def test_get_page_presence_success(client: AsyncClient, test_user, db_session):
    """Test successful page presence retrieval."""
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

    # Create space
    space = SpaceModel(organization_id=org.id, name="Test Space", key="TEST")
    db_session.add(space)
    await db_session.flush()

    # Create page
    page = PageModel(
        space_id=space.id,
        title="Test Page",
        slug="test-page",
        created_by=test_user.id,
    )
    db_session.add(page)
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

    # Get page presence
    get_response = await client.get(f"/api/v1/pages/{page.id}/presence", headers=auth_headers)

    assert get_response.status_code == 200
    data = get_response.json()
    assert "presences" in data
    assert "total" in data
    assert isinstance(data["presences"], list)


@pytest.mark.asyncio
async def test_get_page_presence_not_found(client: AsyncClient, test_user, db_session):
    """Test getting presence for non-existent page."""
    from uuid import uuid4

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

    # Get presence for non-existent page
    get_response = await client.get(f"/api/v1/pages/{uuid4()}/presence", headers=auth_headers)

    assert get_response.status_code == 404
