"""Integration tests for export endpoints."""

import pytest
from httpx import AsyncClient

try:
    import weasyprint  # noqa: F401

    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    PageModel,
    SpaceModel,
)


@pytest.mark.asyncio
@pytest.mark.skipif(
    not WEASYPRINT_AVAILABLE,
    reason="weasyprint not available (missing system dependencies)",
)
async def test_export_page_pdf_success(client: AsyncClient, test_user, db_session):
    """Test successful page export to PDF."""

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
        content="<h1>Test Content</h1><p>This is a test page.</p>",
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

    # Export page to PDF
    export_response = await client.get(f"/api/v1/pages/{page.id}/export/pdf", headers=auth_headers)

    assert export_response.status_code == 200
    assert export_response.headers["content-type"] == "application/pdf"
    assert len(export_response.content) > 0


@pytest.mark.asyncio
async def test_export_page_markdown_success(client: AsyncClient, test_user, db_session):
    """Test successful page export to Markdown."""
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
        content="<h1>Test Content</h1><p>This is a test page.</p>",
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

    # Export page to Markdown
    export_response = await client.get(
        f"/api/v1/pages/{page.id}/export/markdown", headers=auth_headers
    )

    assert export_response.status_code == 200
    assert "text/markdown" in export_response.headers["content-type"]
    assert b"Test Content" in export_response.content


@pytest.mark.asyncio
async def test_export_page_html_success(client: AsyncClient, test_user, db_session):
    """Test successful page export to HTML."""
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
        content="<h1>Test Content</h1><p>This is a test page.</p>",
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

    # Export page to HTML
    export_response = await client.get(f"/api/v1/pages/{page.id}/export/html", headers=auth_headers)

    assert export_response.status_code == 200
    assert "text/html" in export_response.headers["content-type"]
    assert b"Test Content" in export_response.content


@pytest.mark.asyncio
@pytest.mark.skipif(
    not WEASYPRINT_AVAILABLE,
    reason="weasyprint not available (missing system dependencies)",
)
async def test_export_space_pdf_success(client: AsyncClient, test_user, db_session):
    """Test successful space export to PDF."""

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
    page1 = PageModel(
        space_id=space.id,
        title="Page 1",
        slug="page-1",
        content="<h1>Page 1 Content</h1>",
        created_by=test_user.id,
    )
    page2 = PageModel(
        space_id=space.id,
        title="Page 2",
        slug="page-2",
        content="<h1>Page 2 Content</h1>",
        created_by=test_user.id,
    )
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

    # Export space to PDF
    export_response = await client.get(
        f"/api/v1/spaces/{space.id}/export?format=pdf", headers=auth_headers
    )

    assert export_response.status_code == 200
    assert export_response.headers["content-type"] == "application/pdf"
    assert len(export_response.content) > 0


@pytest.mark.asyncio
async def test_export_page_invalid_format(client: AsyncClient, test_user, db_session):
    """Test export with invalid format."""
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

    # Export page with invalid format
    # The use case raises ValueError which is converted to HTTPException 400
    export_response = await client.get(
        f"/api/v1/pages/{page.id}/export/invalid", headers=auth_headers
    )

    # Should return 400 for invalid format
    assert export_response.status_code == 400
