"""Integration tests for search endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    OrganizationMemberModel,
    OrganizationModel,
    ProjectModel,
    SpaceModel,
)


@pytest.mark.asyncio
async def test_search_issues_endpoint(client: AsyncClient, test_user, db_session):
    """Search issues within a project."""
    org = OrganizationModel(name="Search Org", slug=f"search-org-{uuid4().hex[:6]}")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()

    project = ProjectModel(organization_id=org.id, name="Search Project", key="SRCH")
    db_session.add(project)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create issue
    create_issue_response = await client.post(
        "/api/v1/issues/",
        json={
            "project_id": str(project.id),
            "title": "Searchable issue",
            "description": "This issue should appear in search results",
            "type": "bug",
            "status": "todo",
            "priority": "medium",
        },
        headers=headers,
    )
    assert create_issue_response.status_code == 201

    # Search
    search_response = await client.get(
        "/api/v1/search",
        params={
            "query": "Searchable",
            "type": "issues",
            "project_id": str(project.id),
        },
        headers=headers,
    )
    assert search_response.status_code == 200
    data = search_response.json()
    assert data["total"] >= 1
    assert any(item["entity_type"] == "issue" for item in data["items"])


@pytest.mark.asyncio
async def test_search_pages_endpoint(client: AsyncClient, test_user, db_session):
    """Search pages within a space."""
    org = OrganizationModel(name="Search Org 2", slug=f"search-org2-{uuid4().hex[:6]}")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(organization_id=org.id, user_id=test_user.id, role="admin")
    db_session.add(org_member)
    await db_session.flush()

    space = SpaceModel(
        organization_id=org.id,
        name="Search Space",
        key=f"SRCH{uuid4().hex[:3]}",
    )
    db_session.add(space)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email.value, "password": "TestPassword123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create page
    create_page_response = await client.post(
        "/api/v1/pages/",
        json={
            "space_id": str(space.id),
            "title": "Searchable page",
            "content": "This page content should be searchable",
        },
        headers=headers,
    )
    assert create_page_response.status_code == 201

    # Search pages
    search_response = await client.get(
        "/api/v1/search",
        params={
            "query": "searchable",
            "type": "pages",
            "space_id": str(space.id),
        },
        headers=headers,
    )
    assert search_response.status_code == 200
    data = search_response.json()
    assert data["total"] >= 1
    assert any(item["entity_type"] == "page" for item in data["items"])
