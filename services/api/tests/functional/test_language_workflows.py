"""Functional tests for language workflows."""

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    create_test_user,
    get_auth_headers,
)


@pytest.mark.asyncio
async def test_user_language_preference_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test complete user language preference workflow.

    This test covers:
    1. User registration (default language: en)
    2. Getting current language preference
    3. Updating language preference
    4. Verifying the updated preference persists
    """
    # Step 1: Create user
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Language Test User",
    )
    headers = get_auth_headers(user_data["access_token"])

    # Step 2: Get current language (should be default 'en')
    get_response = await client.get("/api/v1/users/me/language", headers=headers)
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["language"] == "en"

    # Step 3: Update language to French
    update_response = await client.put(
        "/api/v1/users/me/language",
        headers=headers,
        json={"language": "fr"},
    )
    assert update_response.status_code == 200
    update_data = update_response.json()
    assert update_data["language"] == "fr"

    # Step 4: Verify the preference persists
    verify_response = await client.get("/api/v1/users/me/language", headers=headers)
    assert verify_response.status_code == 200
    verify_data = verify_response.json()
    assert verify_data["language"] == "fr"


@pytest.mark.asyncio
async def test_list_supported_languages_workflow(
    client: AsyncClient,
) -> None:
    """Test listing supported languages.

    This test verifies that the API returns all supported languages
    with their codes and names, without requiring authentication.
    """
    response = await client.get("/api/v1/languages")

    assert response.status_code == 200
    data = response.json()
    assert "languages" in data

    languages = data["languages"]
    assert len(languages) >= 4  # At least en, fr, es, de

    # Verify all expected languages are present
    language_codes = [lang["code"] for lang in languages]
    assert "en" in language_codes
    assert "fr" in language_codes
    assert "es" in language_codes
    assert "de" in language_codes

    # Verify structure
    for lang in languages:
        assert "code" in lang
        assert "name" in lang
        assert isinstance(lang["code"], str)
        assert isinstance(lang["name"], str)
        assert len(lang["code"]) >= 2


@pytest.mark.asyncio
async def test_multilingual_user_switching_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test user switching between multiple languages.

    This test simulates a user switching their language preference
    multiple times and verifies each change persists correctly.
    """
    # Create user
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Multilingual User",
    )
    headers = get_auth_headers(user_data["access_token"])

    # Test language progression: en -> fr -> es -> de -> en
    languages_to_test = ["fr", "es", "de", "en"]

    for language in languages_to_test:
        # Update to new language
        update_response = await client.put(
            "/api/v1/users/me/language",
            headers=headers,
            json={"language": language},
        )
        assert update_response.status_code == 200
        assert update_response.json()["language"] == language

        # Verify the change
        get_response = await client.get("/api/v1/users/me/language", headers=headers)
        assert get_response.status_code == 200
        assert get_response.json()["language"] == language


@pytest.mark.asyncio
async def test_invalid_language_code_error_handling(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test error handling for invalid language codes.

    This test verifies that the API properly rejects invalid or
    unsupported language codes with appropriate error messages.
    """
    # Create user
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Error Test User",
    )
    headers = get_auth_headers(user_data["access_token"])

    # Test various invalid language codes
    invalid_codes = [
        "invalid",  # Not a valid language code
        "zh",  # Valid code but not supported
        "ja",  # Valid code but not supported
        "x",  # Too short
        "toolongcode",  # Too long
        "",  # Empty
    ]

    for invalid_code in invalid_codes:
        response = await client.put(
            "/api/v1/users/me/language",
            headers=headers,
            json={"language": invalid_code},
        )
        # Should return 400 (Bad Request) or 422 (Validation Error)
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_language_preference_with_region_code_workflow(
    client: AsyncClient,
    unique_email: str,
    test_password: str,
) -> None:
    """Test language preference with region-specific codes.

    This test verifies that the API correctly handles region-specific
    language codes (e.g., 'en-US', 'es-MX') and normalizes them properly.
    """
    # Create user
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Region Code User",
    )
    headers = get_auth_headers(user_data["access_token"])

    # Test region-specific codes
    region_codes = [
        ("en-US", "en-us"),  # (input, expected_output)
        ("es-MX", "es-mx"),
        ("fr-CA", "fr-ca"),
        ("de-CH", "de-ch"),
    ]

    for input_code, expected_output in region_codes:
        # Update with region code
        update_response = await client.put(
            "/api/v1/users/me/language",
            headers=headers,
            json={"language": input_code},
        )
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["language"] == expected_output

        # Verify the preference persists with normalization
        get_response = await client.get("/api/v1/users/me/language", headers=headers)
        assert get_response.status_code == 200
        assert get_response.json()["language"] == expected_output


@pytest.mark.asyncio
async def test_unauthenticated_access_to_protected_endpoints(
    client: AsyncClient,
) -> None:
    """Test that language preference endpoints require authentication.

    This test verifies that endpoints requiring authentication
    properly reject unauthenticated requests.
    """
    # Try to get language preference without authentication
    get_response = await client.get("/api/v1/users/me/language")
    assert get_response.status_code == 401

    # Try to update language preference without authentication
    update_response = await client.put(
        "/api/v1/users/me/language",
        json={"language": "fr"},
    )
    assert update_response.status_code == 401

