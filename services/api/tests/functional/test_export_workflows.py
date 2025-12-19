"""Functional tests for export workflows."""

import pytest
from httpx import AsyncClient

try:
    import weasyprint  # noqa: F401

    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False

from tests.functional.conftest import (
    authenticated_client,
    create_test_organization,
    create_test_page,
    create_test_space,
    create_test_user,
)


@pytest.mark.asyncio
async def test_page_export_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test page export workflow: Create Page → Export to PDF/Markdown/HTML.

    This workflow validates that:
    - Pages can be exported to different formats
    - Export content is correct
    """
    # Step 1: Create organization and space
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
        slug="test-org-export",
    )
    space = await create_test_space(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Space",
    )

    # Step 2: Create page
    page = await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Test Page",
        content="<h1>Test Content</h1><p>This is a test page.</p>",
    )
    page_id = page["id"]

    # Step 3: Export to PDF (skip if weasyprint not available)
    if WEASYPRINT_AVAILABLE:
        pdf_response = await client_instance.get(
            f"/api/v1/pages/{page_id}/export/pdf",
            headers=headers,
        )
        assert pdf_response.status_code == 200
        assert pdf_response.headers["content-type"] == "application/pdf"
        assert len(pdf_response.content) > 0
    else:
        pytest.skip("weasyprint not available (missing system dependencies)")

    # Step 4: Export to Markdown
    md_response = await client_instance.get(
        f"/api/v1/pages/{page_id}/export/markdown",
        headers=headers,
    )
    assert md_response.status_code == 200
    assert md_response.headers["content-type"].startswith("text/markdown")
    assert b"Test Content" in md_response.content

    # Step 5: Export to HTML
    html_response = await client_instance.get(
        f"/api/v1/pages/{page_id}/export/html",
        headers=headers,
    )
    assert html_response.status_code == 200
    assert html_response.headers["content-type"].startswith("text/html")
    assert b"Test Content" in html_response.content


@pytest.mark.asyncio
async def test_space_export_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test space export workflow: Create Space with Pages → Export to PDF.

    This workflow validates that:
    - Spaces can be exported with all pages
    """
    # Step 1: Create organization and space
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
        slug="test-org-space-export",
    )
    space = await create_test_space(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Space",
    )

    # Step 2: Create pages
    await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Page 1",
        content="<h1>Page 1 Content</h1>",
    )
    await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Page 2",
        content="<h1>Page 2 Content</h1>",
    )

    # Step 3: Export space to PDF (skip if weasyprint not available)
    if WEASYPRINT_AVAILABLE:
        pdf_response = await client_instance.get(
            f"/api/v1/spaces/{space['id']}/export?format=pdf",
            headers=headers,
        )
        assert pdf_response.status_code == 200
        assert pdf_response.headers["content-type"] == "application/pdf"
        assert len(pdf_response.content) > 0
    else:
        pytest.skip("weasyprint not available (missing system dependencies)")
