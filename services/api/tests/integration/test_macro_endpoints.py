"""Integration tests for macro endpoints."""

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    MacroModel,
    OrganizationMemberModel,
    OrganizationModel,
)


@pytest.mark.asyncio
async def test_create_macro_success(client: AsyncClient, test_user, db_session):
    """Test successful macro creation."""
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

    # Create macro
    create_response = await client.post(
        "/api/v1/macros/",
        json={
            "name": "Test Macro",
            "code": "return 'Hello, World!';",
            "macro_type": "code_block",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["name"] == "Test Macro"
    assert data["macro_type"] == "code_block"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_macro_success(client: AsyncClient, test_user, db_session):
    """Test successful macro retrieval."""
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

    # Create macro
    macro = MacroModel(
        name="Test Macro",
        code="return 'Hello, World!';",
        macro_type="code_block",
    )
    db_session.add(macro)
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

    # Get macro
    get_response = await client.get(f"/api/v1/macros/{macro.id}", headers=auth_headers)

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(macro.id)
    assert data["name"] == "Test Macro"
    assert data["code"] == "return 'Hello, World!';"


@pytest.mark.asyncio
async def test_list_macros_success(client: AsyncClient, test_user, db_session):
    """Test successful macro listing."""
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

    # Create macros
    macro1 = MacroModel(
        name="Macro 1",
        code="return 'Macro 1';",
        macro_type="code_block",
    )
    macro2 = MacroModel(
        name="Macro 2",
        code="return 'Macro 2';",
        macro_type="code_block",
    )
    db_session.add(macro1)
    db_session.add(macro2)
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

    # List macros
    list_response = await client.get("/api/v1/macros/", headers=auth_headers)

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data["macros"]) == 2
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_update_macro_success(client: AsyncClient, test_user, db_session):
    """Test successful macro update."""
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

    # Create macro
    macro = MacroModel(
        name="Test Macro",
        code="return 'Hello, World!';",
        macro_type="code_block",
    )
    db_session.add(macro)
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

    # Update macro
    update_response = await client.put(
        f"/api/v1/macros/{macro.id}",
        json={
            "name": "Updated Macro",
            "code": "return 'Updated!';",
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Macro"
    assert data["code"] == "return 'Updated!';"


@pytest.mark.asyncio
async def test_delete_macro_success(client: AsyncClient, test_user, db_session):
    """Test successful macro deletion."""
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

    # Create macro
    macro = MacroModel(
        name="Test Macro",
        code="return 'Hello, World!';",
        macro_type="code_block",
    )
    db_session.add(macro)
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

    # Delete macro
    delete_response = await client.delete(f"/api/v1/macros/{macro.id}", headers=auth_headers)

    assert delete_response.status_code == 204

    # Verify macro is deleted
    get_response = await client.get(f"/api/v1/macros/{macro.id}", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_execute_macro_success(client: AsyncClient, test_user, db_session):
    """Test successful macro execution."""
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

    # Create macro
    macro = MacroModel(
        name="Test Macro",
        code="return 'Hello, World!';",
        macro_type="code_block",
    )
    db_session.add(macro)
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

    # Execute macro
    execute_response = await client.post(
        "/api/v1/macros/execute",
        json={
            "macro_name": "Test Macro",
            "config": {},
        },
        headers=auth_headers,
    )

    assert execute_response.status_code == 200
    data = execute_response.json()
    assert "output" in data


@pytest.mark.asyncio
async def test_get_macro_not_found(client: AsyncClient, test_user, db_session):
    """Test getting non-existent macro."""
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

    # Get non-existent macro
    get_response = await client.get(f"/api/v1/macros/{uuid4()}", headers=auth_headers)

    assert get_response.status_code == 404
