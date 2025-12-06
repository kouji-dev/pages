"""Unit tests for avatar upload and deletion use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.use_cases.user import DeleteAvatarUseCase, UploadAvatarUseCase
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.value_objects import Email


class TestUploadAvatarUseCase:
    """Tests for UploadAvatarUseCase."""

    @pytest.fixture
    def password_service(self):
        """Get password service for creating test user."""
        from src.infrastructure.security import BcryptPasswordService

        return BcryptPasswordService()

    @pytest.fixture
    def test_user(self, password_service):
        """Create a test user."""
        from src.domain.value_objects import Password

        password = Password("TestPassword123!")
        hashed_password = password_service.hash(password)
        return User.create(
            email=Email("test@example.com"),
            password_hash=hashed_password,
            name="Test User",
        )

    @pytest.fixture
    def image_bytes(self):
        """Create a simple PNG image for testing."""
        # Create a minimal valid PNG image (1x1 pixel)
        # PNG signature + minimal IHDR chunk
        return bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
            "890000000a49444154789c63000100000500010d0a2db40000000049454e44ae"
            "426082"
        )

    @pytest.mark.asyncio
    async def test_upload_avatar_success(self, test_user, image_bytes) -> None:
        """Test successfully uploading avatar."""
        # Setup
        user_repository = AsyncMock()
        storage_service = AsyncMock()

        user_repository.get_by_id.return_value = test_user
        user_repository.update.return_value = test_user
        storage_service.save.return_value = "http://localhost:8000/storage/avatars/user_id/file.png"

        use_case = UploadAvatarUseCase(user_repository, storage_service)

        # Execute
        result = await use_case.execute(
            user_id=str(test_user.id),
            file_content=image_bytes,
            file_name="avatar.png",
            content_type="image/png",
        )

        # Assert
        assert result.avatar_url is not None
        assert "storage" in result.avatar_url
        user_repository.get_by_id.assert_called_once()
        assert storage_service.save.call_count >= 1  # At least one size saved

    @pytest.mark.asyncio
    async def test_upload_avatar_invalid_mime_type(self, test_user, image_bytes) -> None:
        """Test uploading avatar with invalid MIME type fails."""
        # Setup
        user_repository = AsyncMock()
        storage_service = AsyncMock()
        user_repository.get_by_id.return_value = test_user

        use_case = UploadAvatarUseCase(user_repository, storage_service)

        # Execute & Assert
        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(
                user_id=str(test_user.id),
                file_content=image_bytes,
                file_name="avatar.pdf",
                content_type="application/pdf",
            )

        assert (
            "file type" in str(exc_info.value).lower()
            or "not allowed" in str(exc_info.value).lower()
        )

    @pytest.mark.asyncio
    async def test_upload_avatar_file_too_large(self, test_user, image_bytes) -> None:
        """Test uploading avatar with file too large fails."""
        # Setup
        user_repository = AsyncMock()
        storage_service = AsyncMock()
        user_repository.get_by_id.return_value = test_user

        # Create large file content (over 5MB)
        large_content = image_bytes * (6 * 1024 * 1024)  # 6MB

        use_case = UploadAvatarUseCase(user_repository, storage_service)

        # Execute & Assert
        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(
                user_id=str(test_user.id),
                file_content=large_content,
                file_name="avatar.png",
                content_type="image/png",
                max_size_mb=5,
            )

        assert "size" in str(exc_info.value).lower() or "exceeds" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_upload_avatar_user_not_found(self, image_bytes) -> None:
        """Test uploading avatar for non-existent user."""
        # Setup
        user_repository = AsyncMock()
        storage_service = AsyncMock()
        user_repository.get_by_id.return_value = None

        use_case = UploadAvatarUseCase(user_repository, storage_service)

        # Execute & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(
                user_id=str(uuid4()),
                file_content=image_bytes,
                file_name="avatar.png",
                content_type="image/png",
            )

    @pytest.mark.asyncio
    async def test_upload_avatar_deletes_old_avatar(self, test_user, image_bytes) -> None:
        """Test that uploading new avatar deletes old one."""
        # Setup
        user_repository = AsyncMock()
        storage_service = AsyncMock()

        # Set old avatar URL
        test_user.update_avatar("http://localhost:8000/storage/old_avatar.png")

        user_repository.get_by_id.return_value = test_user
        user_repository.update.return_value = test_user
        storage_service.save.return_value = "http://localhost:8000/storage/new_avatar.png"

        use_case = UploadAvatarUseCase(user_repository, storage_service)

        # Execute
        await use_case.execute(
            user_id=str(test_user.id),
            file_content=image_bytes,
            file_name="avatar.png",
            content_type="image/png",
        )

        # Assert - old avatar should be deleted
        assert storage_service.delete.called


class TestDeleteAvatarUseCase:
    """Tests for DeleteAvatarUseCase."""

    @pytest.fixture
    def password_service(self):
        """Get password service for creating test user."""
        from src.infrastructure.security import BcryptPasswordService

        return BcryptPasswordService()

    @pytest.fixture
    def test_user(self, password_service):
        """Create a test user."""
        from src.domain.value_objects import Password

        password = Password("TestPassword123!")
        hashed_password = password_service.hash(password)
        user = User.create(
            email=Email("test@example.com"),
            password_hash=hashed_password,
            name="Test User",
        )
        user.update_avatar("http://localhost:8000/storage/avatar.png")
        return user

    @pytest.mark.asyncio
    async def test_delete_avatar_success(self, test_user) -> None:
        """Test successfully deleting avatar."""
        # Setup
        user_repository = AsyncMock()
        storage_service = AsyncMock()

        user_repository.get_by_id.return_value = test_user
        user_repository.update.return_value = test_user

        use_case = DeleteAvatarUseCase(user_repository, storage_service)

        # Execute
        result = await use_case.execute(str(test_user.id))

        # Assert
        assert result.avatar_url is None
        user_repository.get_by_id.assert_called_once()
        user_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_avatar_no_avatar(self, password_service) -> None:
        """Test deleting avatar when user has no avatar."""
        # Setup
        from src.domain.value_objects import Password

        password = Password("TestPassword123!")
        hashed_password = password_service.hash(password)
        user_without_avatar = User.create(
            email=Email("test@example.com"),
            password_hash=hashed_password,
            name="Test User",
        )

        user_repository = AsyncMock()
        storage_service = AsyncMock()

        user_repository.get_by_id.return_value = user_without_avatar

        use_case = DeleteAvatarUseCase(user_repository, storage_service)

        # Execute
        result = await use_case.execute(str(user_without_avatar.id))

        # Assert
        assert result.avatar_url is None
        storage_service.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_avatar_user_not_found(self) -> None:
        """Test deleting avatar for non-existent user."""
        # Setup
        user_repository = AsyncMock()
        storage_service = AsyncMock()
        user_repository.get_by_id.return_value = None

        use_case = DeleteAvatarUseCase(user_repository, storage_service)

        # Execute & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))
