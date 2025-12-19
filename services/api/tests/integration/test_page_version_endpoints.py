"""Integration tests for page version endpoints."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    PageModel,
    PageVersionModel,
    SpaceModel,
)


@pytest.mark.asyncio
async def test_list_page_versions_success(client: AsyncClient, test_user, db_session):
    """Test successful page version listing."""
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
        content="Original content",
        created_by=test_user.id,
    )
    db_session.add(page)
    await db_session.flush()

    # Create page versions
    version1 = PageVersionModel(
        page_id=page.id,
        version_number=1,
        title="Test Page",
        content="Version 1 content",
        created_by=test_user.id,
    )
    version2 = PageVersionModel(
        page_id=page.id,
        version_number=2,
        title="Test Page",
        content="Version 2 content",
        created_by=test_user.id,
    )
    db_session.add(version1)
    db_session.add(version2)
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

    # List page versions
    list_response = await client.get(f"/api/v1/pages/{page.id}/versions", headers=auth_headers)

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["versions"]) == 2
    assert data["total"] == 2
    assert data["versions"][0]["version_number"] == 2  # Latest first
    assert data["versions"][1]["version_number"] == 1


@pytest.mark.asyncio
async def test_get_page_version_success(client: AsyncClient, test_user, db_session):
    """Test successful page version retrieval."""
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
        content="Original content",
        created_by=test_user.id,
    )
    db_session.add(page)
    await db_session.flush()

    # Create page version
    version = PageVersionModel(
        page_id=page.id,
        version_number=1,
        title="Test Page",
        content="Version 1 content",
        created_by=test_user.id,
    )
    db_session.add(version)
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

    # Get page version
    get_response = await client.get(f"/api/v1/page-versions/{version.id}", headers=auth_headers)

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(version.id)
    assert data["version_number"] == 1
    assert data["title"] == "Test Page"
    assert data["content"] == "Version 1 content"


@pytest.mark.asyncio
async def test_restore_page_version_success(client: AsyncClient, test_user, db_session):
    """Test successful page version restoration."""
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
        content="Current content",
        created_by=test_user.id,
    )
    db_session.add(page)
    await db_session.flush()

    # Create page version
    version = PageVersionModel(
        page_id=page.id,
        version_number=1,
        title="Test Page",
        content="Old content to restore",
        created_by=test_user.id,
    )
    db_session.add(version)
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

    # Restore page version
    restore_response = await client.post(
        f"/api/v1/page-versions/{version.id}/restore", headers=auth_headers
    )

    assert restore_response.status_code == 200
    data = restore_response.json()
    assert data["page_id"] == str(page.id)
    assert data["restored_version_id"] == str(version.id)
    assert "new_version_id" in data
    assert "message" in data

    # Verify new version was created
    await db_session.refresh(page)
    list_response = await client.get(f"/api/v1/pages/{page.id}/versions", headers=auth_headers)
    assert list_response.status_code == 200
    versions_data = list_response.json()
    assert versions_data["total"] == 2  # Original + restored


@pytest.mark.asyncio
async def test_get_page_version_diff_success(client: AsyncClient, test_user, db_session):
    """Test successful page version diff retrieval."""
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
        content="Current content",
        created_by=test_user.id,
    )
    db_session.add(page)
    await db_session.flush()

    # Create page versions
    version1 = PageVersionModel(
        page_id=page.id,
        version_number=1,
        title="Test Page",
        content="Version 1 content",
        created_by=test_user.id,
    )
    version2 = PageVersionModel(
        page_id=page.id,
        version_number=2,
        title="Test Page",
        content="Version 2 content",
        created_by=test_user.id,
    )
    db_session.add(version1)
    db_session.add(version2)
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

    # Get diff
    diff_response = await client.get(
        f"/api/v1/page-versions/{version2.id}/diff?compare_with={version1.id}",
        headers=auth_headers,
    )

    assert diff_response.status_code == 200
    data = diff_response.json()
    assert "title_diff" in data
    assert "content_diff" in data


@pytest.mark.asyncio
async def test_list_page_versions_empty(client: AsyncClient, test_user, db_session):
    """Test listing page versions for page with no versions."""
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

    # List page versions
    list_response = await client.get(f"/api/v1/pages/{page.id}/versions", headers=auth_headers)

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["versions"]) == 0
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_get_page_version_not_found(client: AsyncClient, test_user, db_session):
    """Test getting non-existent page version."""
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

    # Get non-existent page version
    get_response = await client.get(f"/api/v1/page-versions/{uuid4()}", headers=auth_headers)

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_list_page_versions_pagination(client: AsyncClient, test_user, db_session):
    """Test page version listing with pagination."""
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

    # Create multiple page versions
    for i in range(5):
        version = PageVersionModel(
            page_id=page.id,
            version_number=i + 1,
            title="Test Page",
            content=f"Version {i + 1} content",
            created_by=test_user.id,
        )
        db_session.add(version)
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

    # List page versions with pagination
    list_response = await client.get(
        f"/api/v1/pages/{page.id}/versions?skip=0&limit=2", headers=auth_headers
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["versions"]) == 2
    assert data["total"] == 5
