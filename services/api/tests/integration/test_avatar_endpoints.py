"""Integration tests for avatar upload and deletion endpoints."""

import io

import pytest
from httpx import AsyncClient
from PIL import Image

from src.domain.entities import User


def create_test_image(format: str = "PNG", size: tuple[int, int] = (200, 200)) -> bytes:
    """Create a test image in memory.

    Args:
        format: Image format (PNG, JPEG, WEBP)
        size: Image size in pixels (width, height)

    Returns:
        Image file content as bytes
    """
    # Create a simple colored image
    img = Image.new("RGB", size, color=(73, 109, 137))

    # Save to bytes
    output = io.BytesIO()
    if format == "JPEG":
        img.save(output, format="JPEG", quality=95)
    elif format == "WEBP":
        img.save(output, format="WEBP", quality=95)
    else:  # PNG
        img.save(output, format="PNG")

    output.seek(0)
    return output.read()


@pytest.mark.asyncio
async def test_upload_avatar_success(client: AsyncClient, test_user: User) -> None:
    """Test successfully uploading avatar."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Create test image
    image_bytes = create_test_image("PNG")

    # Upload avatar
    files = {"file": ("avatar.png", image_bytes, "image/png")}
    response = await client.post(
        "/api/v1/users/me/avatar",
        headers={"Authorization": f"Bearer {access_token}"},
        files=files,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["avatar_url"] is not None
    assert "storage" in data["avatar_url"]
    assert data["id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_upload_avatar_jpeg(client: AsyncClient, test_user: User) -> None:
    """Test uploading JPEG avatar."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Create test JPEG image
    image_bytes = create_test_image("JPEG")

    # Upload avatar
    files = {"file": ("avatar.jpg", image_bytes, "image/jpeg")}
    response = await client.post(
        "/api/v1/users/me/avatar",
        headers={"Authorization": f"Bearer {access_token}"},
        files=files,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["avatar_url"] is not None


@pytest.mark.asyncio
async def test_upload_avatar_requires_auth(client: AsyncClient) -> None:
    """Test that uploading avatar requires authentication."""
    image_bytes = create_test_image()

    files = {"file": ("avatar.png", image_bytes, "image/png")}
    response = await client.post(
        "/api/v1/users/me/avatar",
        files=files,
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_avatar_invalid_file_type(client: AsyncClient, test_user: User) -> None:
    """Test that uploading non-image file fails."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Try to upload PDF file
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\ntrailer\n<< /Size 1 >>\nstartxref\n9\n%%EOF"

    files = {"file": ("document.pdf", pdf_content, "application/pdf")}
    response = await client.post(
        "/api/v1/users/me/avatar",
        headers={"Authorization": f"Bearer {access_token}"},
        files=files,
    )

    assert response.status_code == 400 or response.status_code == 422
    error_data = response.json()
    error_text = error_data.get("message", "").lower()
    assert "file type" in error_text or "not allowed" in error_text


@pytest.mark.asyncio
async def test_upload_avatar_file_too_large(client: AsyncClient, test_user: User) -> None:
    """Test that uploading file that's too large fails."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Create a large image (over 5MB)
    # Create a large image by repeating a smaller one
    small_image = create_test_image("PNG", (100, 100))
    large_image = small_image * (6 * 1024 * 1024 // len(small_image) + 1)  # ~6MB

    files = {"file": ("large_avatar.png", large_image, "image/png")}
    response = await client.post(
        "/api/v1/users/me/avatar",
        headers={"Authorization": f"Bearer {access_token}"},
        files=files,
    )

    assert response.status_code == 400 or response.status_code == 422
    error_data = response.json()
    error_text = error_data.get("message", "").lower()
    assert "size" in error_text or "exceeds" in error_text


@pytest.mark.asyncio
async def test_delete_avatar_success(client: AsyncClient, test_user: User) -> None:
    """Test successfully deleting avatar."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # First upload an avatar
    image_bytes = create_test_image()
    files = {"file": ("avatar.png", image_bytes, "image/png")}
    upload_response = await client.post(
        "/api/v1/users/me/avatar",
        headers={"Authorization": f"Bearer {access_token}"},
        files=files,
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["avatar_url"] is not None

    # Delete avatar
    response = await client.delete(
        "/api/v1/users/me/avatar",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["avatar_url"] is None
    assert data["id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_delete_avatar_no_avatar(client: AsyncClient, test_user: User) -> None:
    """Test deleting avatar when user has no avatar."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Delete avatar (should succeed even if no avatar exists)
    response = await client.delete(
        "/api/v1/users/me/avatar",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["avatar_url"] is None


@pytest.mark.asyncio
async def test_delete_avatar_requires_auth(client: AsyncClient) -> None:
    """Test that deleting avatar requires authentication."""
    response = await client.delete("/api/v1/users/me/avatar")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_avatar_replaces_existing(client: AsyncClient, test_user: User) -> None:
    """Test that uploading new avatar replaces existing one."""
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Upload first avatar
    image_bytes_1 = create_test_image("PNG", (100, 100))
    files_1 = {"file": ("avatar1.png", image_bytes_1, "image/png")}
    upload_1_response = await client.post(
        "/api/v1/users/me/avatar",
        headers={"Authorization": f"Bearer {access_token}"},
        files=files_1,
    )
    assert upload_1_response.status_code == 200
    first_avatar_url = upload_1_response.json()["avatar_url"]
    assert first_avatar_url is not None

    # Upload second avatar (should replace first)
    image_bytes_2 = create_test_image("PNG", (150, 150))
    files_2 = {"file": ("avatar2.png", image_bytes_2, "image/png")}
    upload_2_response = await client.post(
        "/api/v1/users/me/avatar",
        headers={"Authorization": f"Bearer {access_token}"},
        files=files_2,
    )
    assert upload_2_response.status_code == 200
    second_avatar_url = upload_2_response.json()["avatar_url"]
    assert second_avatar_url is not None
    assert second_avatar_url != first_avatar_url

    # Verify profile shows new avatar
    profile_response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["avatar_url"] == second_avatar_url
