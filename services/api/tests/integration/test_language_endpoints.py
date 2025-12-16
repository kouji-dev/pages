"""Integration tests for language endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import User


@pytest.mark.asyncio
async def test_list_supported_languages(client: AsyncClient) -> None:
    """Test listing supported languages (no auth required)."""
    response = await client.get("/api/v1/languages")

    assert response.status_code == 200
    data = response.json()
    assert "languages" in data
    assert len(data["languages"]) == 4  # en, fr, es, de

    language_codes = [lang["code"] for lang in data["languages"]]
    assert "en" in language_codes
    assert "fr" in language_codes
    assert "es" in language_codes
    assert "de" in language_codes

    # Check structure of each language
    for lang in data["languages"]:
        assert "code" in lang
        assert "name" in lang


@pytest.mark.asyncio
async def test_get_user_language_success(
    client: AsyncClient,
    test_user: User,
    auth_headers_regular: dict[str, str],
) -> None:
    """Test getting user language preference."""
    response = await client.get("/api/v1/users/me/language", headers=auth_headers_regular)

    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"  # Default language
    assert "message" in data


@pytest.mark.asyncio
async def test_get_user_language_unauthorized(client: AsyncClient) -> None:
    """Test getting user language without authentication."""
    response = await client.get("/api/v1/users/me/language")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_language_success(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers_regular: dict[str, str],
) -> None:
    """Test updating user language preference."""
    from src.infrastructure.database.repositories import SQLAlchemyUserRepository

    # Update to French
    response = await client.put(
        "/api/v1/users/me/language",
        headers=auth_headers_regular,
        json={"language": "fr"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "fr"
    assert "message" in data

    # Verify in database
    user_repository = SQLAlchemyUserRepository(db_session)
    updated_user = await user_repository.get_by_id(test_user.id)
    assert updated_user is not None
    assert str(updated_user.language) == "fr"


@pytest.mark.asyncio
async def test_update_user_language_with_region_code(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers_regular: dict[str, str],
) -> None:
    """Test updating user language with region code."""
    from src.infrastructure.database.repositories import SQLAlchemyUserRepository

    response = await client.put(
        "/api/v1/users/me/language",
        headers=auth_headers_regular,
        json={"language": "es-MX"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "es-mx"  # Normalized to lowercase

    # Verify in database
    user_repository = SQLAlchemyUserRepository(db_session)
    updated_user = await user_repository.get_by_id(test_user.id)
    assert updated_user is not None
    assert str(updated_user.language) == "es-mx"


@pytest.mark.asyncio
async def test_update_user_language_invalid_code(
    client: AsyncClient,
    test_user: User,
    auth_headers_regular: dict[str, str],
) -> None:
    """Test updating user language with invalid language code."""
    response = await client.put(
        "/api/v1/users/me/language",
        headers=auth_headers_regular,
        json={"language": "invalid"},
    )

    assert response.status_code == 400 or response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_language_unsupported_code(
    client: AsyncClient,
    test_user: User,
    auth_headers_regular: dict[str, str],
) -> None:
    """Test updating user language with unsupported language code."""
    response = await client.put(
        "/api/v1/users/me/language",
        headers=auth_headers_regular,
        json={"language": "zh"},  # Chinese not supported
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_user_language_unauthorized(client: AsyncClient) -> None:
    """Test updating user language without authentication."""
    response = await client.put(
        "/api/v1/users/me/language",
        json={"language": "fr"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_language_multiple_times(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers_regular: dict[str, str],
) -> None:
    """Test updating user language multiple times."""
    from src.infrastructure.database.repositories import SQLAlchemyUserRepository

    # Update to French
    response1 = await client.put(
        "/api/v1/users/me/language",
        headers=auth_headers_regular,
        json={"language": "fr"},
    )
    assert response1.status_code == 200
    assert response1.json()["language"] == "fr"

    # Update to Spanish
    response2 = await client.put(
        "/api/v1/users/me/language",
        headers=auth_headers_regular,
        json={"language": "es"},
    )
    assert response2.status_code == 200
    assert response2.json()["language"] == "es"

    # Update to German
    response3 = await client.put(
        "/api/v1/users/me/language",
        headers=auth_headers_regular,
        json={"language": "de"},
    )
    assert response3.status_code == 200
    assert response3.json()["language"] == "de"

    # Verify final state in database
    user_repository = SQLAlchemyUserRepository(db_session)
    final_user = await user_repository.get_by_id(test_user.id)
    assert final_user is not None
    assert str(final_user.language) == "de"


@pytest.mark.asyncio
async def test_get_user_language_after_update(
    client: AsyncClient,
    test_user: User,
    auth_headers_regular: dict[str, str],
) -> None:
    """Test getting user language after updating it."""
    # Update language
    update_response = await client.put(
        "/api/v1/users/me/language",
        headers=auth_headers_regular,
        json={"language": "de"},
    )
    assert update_response.status_code == 200

    # Get language
    get_response = await client.get("/api/v1/users/me/language", headers=auth_headers_regular)
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["language"] == "de"
