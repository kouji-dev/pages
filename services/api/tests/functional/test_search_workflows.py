"""Tests fonctionnels pour la recherche (issues, pages, unifiée)."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    authenticated_client,
    create_test_issue,
    create_test_organization,
    create_test_page,
    create_test_project,
    create_test_space,
    create_test_user,
)


@pytest.mark.asyncio
async def test_search_issues_functional(
    client: AsyncClient, unique_email: str, test_password: str
) -> None:
    """Vérifie la recherche d'issues au niveau projet."""
    user_data = await create_test_user(client, unique_email, test_password, "Search User")
    client_instance, headers, _ = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance, headers, name="Search Org Issues", slug="search-org-issues"
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Search Project",
        key="SRCH",
    )

    # Crée deux issues contenant le terme "Recherche"
    await create_test_issue(
        client_instance,
        headers,
        project_id=project["id"],
        title="Recherche API",
        description="Doit apparaitre dans les résultats",
    )
    await create_test_issue(
        client_instance,
        headers,
        project_id=project["id"],
        title="Autre ticket",
        description="Contient Recherche dans la description",
    )

    response = await client_instance.get(
        "/api/v1/issues/search",
        params={
            "project_id": project["id"],
            "query": "Recherche",
            "page": 1,
            "limit": 10,
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert all(item["entity_type"] == "issue" for item in data["items"])


@pytest.mark.asyncio
async def test_search_pages_functional(
    client: AsyncClient, unique_email: str, test_password: str
) -> None:
    """Vérifie la recherche de pages au niveau space."""
    user_data = await create_test_user(client, unique_email, test_password, "Search User")
    client_instance, headers, _ = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance, headers, name="Search Org Pages", slug="search-org-pages"
    )
    space = await create_test_space(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Search Space",
        key="SRCHSP",
    )

    await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Page de Recherche",
        content="Cette page doit être retrouvée",
    )

    response = await client_instance.get(
        "/api/v1/pages/search",
        params={
            "space_id": space["id"],
            "query": "Recherche",
            "page": 1,
            "limit": 10,
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert all(item["entity_type"] == "page" for item in data["items"])


@pytest.mark.asyncio
async def test_unified_search_functional(
    client: AsyncClient, unique_email: str, test_password: str
) -> None:
    """Vérifie la recherche unifiée issues + pages."""
    user_data = await create_test_user(client, unique_email, test_password, "Search User")
    client_instance, headers, _ = await authenticated_client(client, user_data)
    org = await create_test_organization(
        client_instance, headers, name="Search Org Unified", slug="search-org-unified"
    )
    project = await create_test_project(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Search Project Unified",
        key="SRCHU",
    )
    space = await create_test_space(
        client_instance,
        headers,
        organization_id=org["id"],
        name="Search Space Unified",
        key="SRCHSU",
    )

    await create_test_issue(
        client_instance,
        headers,
        project_id=project["id"],
        title="Unifié côté issue",
        description="Recherche Unifiée",
    )
    await create_test_page(
        client_instance,
        headers,
        space_id=space["id"],
        title="Unifié côté page",
        content="Recherche Unifiée dans le contenu",
    )

    response = await client_instance.get(
        "/api/v1/search",
        params={
            "query": "Unifié",
            "type": "all",
            "project_id": project["id"],
            "space_id": space["id"],
            "page": 1,
            "limit": 10,
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    types = {item["entity_type"] for item in data["items"]}
    assert "issue" in types
    assert "page" in types
