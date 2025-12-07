"""Integration tests for page endpoints."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    PageModel,
    SpaceModel,
)


@pytest.mark.asyncio
async def test_create_page_success(client: AsyncClient, test_user, db_session):
    """Test successful page creation."""
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

    # Create page
    create_response = await client.post(
        "/api/v1/pages/",
        json={
            "space_id": str(space.id),
            "title": "My New Page",
            "content": "Page content",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["title"] == "My New Page"
    assert data["content"] == "Page content"
    assert data["space_id"] == str(space.id)
    assert data["comment_count"] == 0
    assert "id" in data


@pytest.mark.asyncio
async def test_create_page_with_parent(client: AsyncClient, test_user, db_session):
    """Test page creation with parent."""
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

    # Create parent page
    parent_page = PageModel(
        space_id=space.id,
        title="Parent Page",
        slug="parent-page",
        created_by=test_user.id,
    )
    db_session.add(parent_page)
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

    # Create child page
    create_response = await client.post(
        "/api/v1/pages/",
        json={
            "space_id": str(space.id),
            "title": "Child Page",
            "parent_id": str(parent_page.id),
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["title"] == "Child Page"
    assert data["parent_id"] == str(parent_page.id)


@pytest.mark.asyncio
async def test_get_page_success(client: AsyncClient, test_user, db_session):
    """Test successful page retrieval."""
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
        content="Test content",
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

    # Get page
    get_response = await client.get(f"/api/v1/pages/{page.id}", headers=auth_headers)

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(page.id)
    assert data["title"] == "Test Page"
    assert data["content"] == "Test content"


@pytest.mark.asyncio
async def test_list_pages_success(client: AsyncClient, test_user, db_session):
    """Test successful page listing."""
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

    # Create pages
    page1 = PageModel(space_id=space.id, title="Page 1", slug="page-1", created_by=test_user.id)
    page2 = PageModel(space_id=space.id, title="Page 2", slug="page-2", created_by=test_user.id)
    db_session.add(page1)
    db_session.add(page2)
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

    # List pages
    list_response = await client.get(f"/api/v1/pages/?space_id={space.id}", headers=auth_headers)

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["pages"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_get_page_tree_success(client: AsyncClient, test_user, db_session):
    """Test successful page tree retrieval."""
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

    # Create pages with hierarchy
    root_page = PageModel(
        space_id=space.id, title="Root Page", slug="root-page", created_by=test_user.id
    )
    db_session.add(root_page)
    await db_session.flush()

    child_page = PageModel(
        space_id=space.id,
        title="Child Page",
        slug="child-page",
        parent_id=root_page.id,
        created_by=test_user.id,
    )
    db_session.add(child_page)
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

    # Get page tree
    tree_response = await client.get(f"/api/v1/pages/spaces/{space.id}/tree", headers=auth_headers)

    assert tree_response.status_code == 200
    data = tree_response.json()
    assert len(data["pages"]) == 1  # Only root pages
    assert data["pages"][0]["title"] == "Root Page"
    assert len(data["pages"][0]["children"]) == 1
    assert data["pages"][0]["children"][0]["title"] == "Child Page"


@pytest.mark.asyncio
async def test_update_page_success(client: AsyncClient, test_user, db_session):
    """Test successful page update."""
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

    # Update page
    update_response = await client.put(
        f"/api/v1/pages/{page.id}",
        json={
            "title": "Updated Page",
            "content": "Updated content",
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated Page"
    assert data["content"] == "Updated content"


@pytest.mark.asyncio
async def test_delete_page_success(client: AsyncClient, test_user, db_session):
    """Test successful page deletion."""
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

    # Delete page (user is author, so can delete)
    delete_response = await client.delete(f"/api/v1/pages/{page.id}", headers=auth_headers)

    assert delete_response.status_code == 204

    # Verify page is soft-deleted (should not appear in list)
    list_response = await client.get(f"/api/v1/pages/?space_id={space.id}", headers=auth_headers)
    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 0
