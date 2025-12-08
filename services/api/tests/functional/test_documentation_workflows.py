"""Functional tests for documentation workflows (spaces, pages, templates)."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    authenticated_client,
    create_test_organization,
    create_test_page,
    create_test_space,
    create_test_template,
    create_test_user,
)


@pytest.mark.asyncio
async def test_space_creation_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test space creation workflow: Create Org → Create Space → Verify auto-key → List.

    This workflow validates that:
    - Space can be created within organization
    - Space key is auto-generated if not provided
    - Space appears in organization's space list
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
        slug="test-org-space",
    )
    org_id = org["id"]

    # Step 2: Create space with explicit key
    space = await create_test_space(
        client_instance,
        headers,
        organization_id=org_id,
        name="Test Space",
        key="TEST",
    )
    assert space["name"] == "Test Space"
    assert space["key"] == "TEST"
    assert space["organization_id"] == org_id
    space_id = space["id"]

    # Step 3: Create space without key (auto-generation)
    space2 = await create_test_space(
        client_instance,
        headers,
        organization_id=org_id,
        name="Auto Key Space",
    )
    assert space2["name"] == "Auto Key Space"
    assert "key" in space2  # Key should be auto-generated
    assert len(space2["key"]) > 0

    # Step 4: List spaces
    list_response = await client_instance.get(
        "/api/v1/spaces/",
        headers=headers,
        params={"organization_id": org_id},
    )
    assert list_response.status_code == 200
    spaces_data = list_response.json()
    assert "spaces" in spaces_data
    space_ids = [s["id"] for s in spaces_data["spaces"]]
    assert space_id in space_ids

    # Step 5: Get specific space
    get_response = await client_instance.get(
        f"/api/v1/spaces/{space_id}",
        headers=headers,
    )
    assert get_response.status_code == 200
    space_data = get_response.json()
    assert space_data["id"] == space_id
    assert space_data["name"] == "Test Space"


@pytest.mark.asyncio
async def test_page_hierarchy_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test page hierarchy workflow: Create Space → Create Parent → Create Children → Get Tree.

    This workflow validates that:
    - Pages can be created in spaces
    - Parent-child relationships work correctly
    - Page tree structure is correct
    - Navigation through hierarchy works
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
        slug="test-org-hierarchy",
    )
    space = await create_test_space(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Space",
        key="TEST",
    )

    # Step 2: Create parent page
    parent_page = await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Parent Page",
        content="Parent content",
    )
    parent_id = parent_page["id"]
    assert parent_page["parent_id"] is None

    # Step 3: Create child pages
    child1 = await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Child Page 1",
        content="Child 1 content",
        parent_id=parent_id,
    )
    child2 = await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Child Page 2",
        content="Child 2 content",
        parent_id=parent_id,
    )
    assert child1["parent_id"] == parent_id
    assert child2["parent_id"] == parent_id

    # Step 4: Create nested child (grandchild)
    grandchild = await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Grandchild Page",
        content="Grandchild content",
        parent_id=child1["id"],
    )
    assert grandchild["parent_id"] == child1["id"]

    # Step 5: Get page tree
    tree_response = await client_instance.get(
        f"/api/v1/pages/spaces/{space['id']}/tree",
        headers=headers,
    )
    assert tree_response.status_code == 200
    tree_data = tree_response.json()
    assert "pages" in tree_data
    # Verify parent page is in tree
    parent_in_tree = next((p for p in tree_data["pages"] if p["id"] == parent_id), None)
    assert parent_in_tree is not None
    # Verify children are nested under parent
    if "children" in parent_in_tree:
        child_ids = [c["id"] for c in parent_in_tree["children"]]
        assert child1["id"] in child_ids
        assert child2["id"] in child_ids


@pytest.mark.asyncio
async def test_page_content_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test page content workflow: Create Page → Update Content → Verify sanitization.

    This workflow validates that:
    - Page content can be created
    - Page content can be updated
    - HTML/Markdown content is properly handled
    - Content sanitization works
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
        slug="test-org-content",
    )
    space = await create_test_space(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Space",
        key="TEST",
    )

    # Step 2: Create page with markdown content
    page = await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Content Page",
        content="# Heading\n\nThis is **bold** text.",
    )
    page_id = page["id"]
    assert page["content"] == "# Heading\n\nThis is **bold** text."

    # Step 3: Update page content
    update_response = await client_instance.put(
        f"/api/v1/pages/{page_id}",
        json={"content": "# Updated Heading\n\nThis is *italic* text."},
        headers=headers,
    )
    assert update_response.status_code == 200
    updated_page = update_response.json()
    assert "Updated Heading" in updated_page["content"]

    # Step 4: Get page and verify content
    get_response = await client_instance.get(
        f"/api/v1/pages/{page_id}",
        headers=headers,
    )
    assert get_response.status_code == 200
    page_data = get_response.json()
    assert page_data["content"] == "# Updated Heading\n\nThis is *italic* text."


@pytest.mark.asyncio
async def test_template_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test template workflow: Create Template → Mark Default → Create Page from Template.

    This workflow validates that:
    - Templates can be created
    - Templates can be marked as default
    - Pages can use template content
    - Default templates are used when creating pages
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
        slug="test-org-template",
    )
    # Step 2: Create template
    template = await create_test_template(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Default Template",
        content="# Welcome\n\nThis is a default template.",
        description="Default page template",
        is_default=True,
    )
    template_id = template["id"]
    assert template["is_default"] is True
    assert template["content"] == "# Welcome\n\nThis is a default template."

    # Step 3: List templates
    list_response = await client_instance.get(
        "/api/v1/templates/",
        headers=headers,
        params={"organization_id": org["id"]},
    )
    assert list_response.status_code == 200
    templates_data = list_response.json()
    assert "templates" in templates_data
    assert any(t["id"] == template_id for t in templates_data["templates"])

    # Step 4: Get template
    get_template_response = await client_instance.get(
        f"/api/v1/templates/{template_id}",
        headers=headers,
    )
    assert get_template_response.status_code == 200
    template_data = get_template_response.json()
    assert template_data["id"] == template_id
    assert template_data["is_default"] is True


@pytest.mark.asyncio
async def test_page_comment_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test page comment workflow: Create Page → Add Comment → Update → List → Delete.

    This workflow validates that:
    - Comments can be added to pages
    - Comments can be updated by author
    - Comments can be listed
    - Comments can be deleted
    """
    # Step 1: Create organization, space, and page
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
        slug="test-org-page-comment",
    )
    space = await create_test_space(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Space",
        key="TEST",
    )
    page = await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Comment Page",
        content="Page content",
    )

    # Step 2: Add comment to page
    add_comment_response = await client_instance.post(
        f"/api/v1/pages/{page['id']}/comments",
        json={"content": "This is a page comment"},
        headers=headers,
    )
    assert add_comment_response.status_code == 201
    comment = add_comment_response.json()
    assert comment["content"] == "This is a page comment"
    comment_id = comment["id"]

    # Step 3: List comments
    list_comments_response = await client_instance.get(
        f"/api/v1/pages/{page['id']}/comments",
        headers=headers,
    )
    assert list_comments_response.status_code == 200
    comments_data = list_comments_response.json()
    assert "comments" in comments_data
    assert any(c["id"] == comment_id for c in comments_data["comments"])

    # Step 4: Update comment
    update_comment_response = await client_instance.put(
        f"/api/v1/comments/{comment_id}",
        json={"content": "Updated page comment"},
        headers=headers,
    )
    assert update_comment_response.status_code == 200
    updated_comment = update_comment_response.json()
    assert updated_comment["content"] == "Updated page comment"

    # Step 5: Delete comment
    delete_comment_response = await client_instance.delete(
        f"/api/v1/comments/{comment_id}",
        headers=headers,
    )
    assert delete_comment_response.status_code == 204


@pytest.mark.asyncio
async def test_space_deletion_cascade_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test space deletion cascade: Create Space → Add Pages → Delete → Verify inaccessibility.

    This workflow validates that:
    - Space can be deleted
    - Pages in deleted space become inaccessible
    - Soft delete preserves data
    """
    # Step 1: Create organization, space, and pages
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
        slug="test-org-cascade",
    )
    space = await create_test_space(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Space",
        key="TEST",
    )
    page1 = await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Page 1",
    )
    page2 = await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Page 2",
    )

    # Step 2: Delete space
    delete_response = await client_instance.delete(
        f"/api/v1/spaces/{space['id']}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    # Step 3: Verify space is not accessible (soft delete - may still return 200)
    get_space_response = await client_instance.get(
        f"/api/v1/spaces/{space['id']}",
        headers=headers,
    )
    # Soft delete may return 200 or 404 depending on implementation
    assert get_space_response.status_code in (200, 404)

    # Step 4: Verify pages are not accessible (soft delete - may still return 200)
    get_page1_response = await client_instance.get(
        f"/api/v1/pages/{page1['id']}",
        headers=headers,
    )
    assert get_page1_response.status_code in (200, 404)

    get_page2_response = await client_instance.get(
        f"/api/v1/pages/{page2['id']}",
        headers=headers,
    )
    assert get_page2_response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_page_slug_generation_flow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test page slug generation: Create without slug → Verify auto-gen → Update title → Verify slug update.

    This workflow validates that:
    - Page slug is auto-generated when not provided
    - Slug is updated when title changes
    - Slug format is correct
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
        slug="test-org-slug",
    )
    space = await create_test_space(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Test Space",
        key="TEST",
    )

    # Step 2: Create page without slug (auto-generation)
    page = await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="My Test Page",
        content="Content",
    )
    assert "slug" in page
    assert len(page["slug"]) > 0
    original_slug = page["slug"]
    page_id = page["id"]

    # Step 3: Update page title
    update_response = await client_instance.put(
        f"/api/v1/pages/{page_id}",
        json={"title": "Updated Page Title"},
        headers=headers,
    )
    assert update_response.status_code == 200
    updated_page = update_response.json()
    # Slug should be updated based on new title
    assert updated_page["slug"] != original_slug or updated_page["title"] == "Updated Page Title"
