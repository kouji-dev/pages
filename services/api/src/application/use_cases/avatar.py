"""Avatar upload and deletion use cases."""

import structlog
from pathlib import Path
from uuid import uuid4

from src.application.dtos.user import UserResponse
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException, StorageException, ValidationException
from src.domain.repositories import UserRepository
from src.domain.services import StorageService
from src.infrastructure.services.image_service import ImageProcessingService

logger = structlog.get_logger()


class UploadAvatarUseCase:
    """Use case for uploading user avatar."""

    def __init__(
        self,
        user_repository: UserRepository,
        storage_service: StorageService,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            user_repository: User repository for data access
            storage_service: Storage service for file operations
        """
        self._user_repository = user_repository
        self._storage_service = storage_service

    async def execute(
        self,
        user_id: str,
        file_content: bytes,
        file_name: str,
        content_type: str,
        max_size_mb: int = 5,
    ) -> UserResponse:
        """Execute avatar upload.

        Args:
            user_id: Current user ID
            file_content: Avatar image file content as bytes
            file_name: Original file name
            content_type: MIME type of the file
            max_size_mb: Maximum file size in MB (default: 5)

        Returns:
            Updated user profile response DTO

        Raises:
            EntityNotFoundException: If user not found
            ValidationException: If file validation fails
            StorageException: If storage operation fails
        """
        from uuid import UUID

        logger.info("Uploading avatar", user_id=user_id, file_name=file_name, content_type=content_type)

        user_uuid = UUID(user_id)
        user = await self._user_repository.get_by_id(user_uuid)

        if user is None:
            logger.warning("User not found for avatar upload", user_id=user_id)
            raise EntityNotFoundException("User", user_id)

        # Validate MIME type
        if not ImageProcessingService.is_allowed_mime_type(content_type):
            raise ValidationException(
                f"File type not allowed. Allowed types: {', '.join(ImageProcessingService.ALLOWED_MIME_TYPES)}",
                field="file",
            )

        # Validate image
        ImageProcessingService.validate_image(file_content, max_size_mb=max_size_mb)

        # Delete old avatar if exists
        if user.avatar_url:
            try:
                # Extract path from URL
                old_path = self._extract_path_from_url(user.avatar_url)
                await self._storage_service.delete(old_path)
                logger.info("Old avatar deleted", path=old_path)
            except Exception as e:
                logger.warning("Failed to delete old avatar", error=str(e))
                # Continue with upload even if deletion fails

        # Process image and create multiple sizes
        output_format = ImageProcessingService.get_output_format(content_type)
        processed_images = ImageProcessingService.process_avatar(file_content, output_format=output_format)

        # Save all sizes to storage
        file_extension = Path(file_name).suffix or ".png"
        base_filename = f"avatars/{user_id}/{uuid4().hex}"
        
        saved_urls = {}
        for size_name, processed_content in processed_images.items():
            file_path = f"{base_filename}_{size_name}{file_extension}"
            url = await self._storage_service.save(processed_content, file_path, content_type)
            saved_urls[size_name] = url

        # Use 256x256 as the main avatar URL (largest size)
        avatar_url = saved_urls.get("256x256", saved_urls.get(list(saved_urls.keys())[0]))

        # Update user avatar URL
        user.update_avatar(avatar_url)
        updated_user = await self._user_repository.update(user)

        logger.info("Avatar uploaded", user_id=user_id, avatar_url=avatar_url)

        return UserResponse(
            id=updated_user.id,
            email=updated_user.email.value,
            name=updated_user.name,
            avatar_url=updated_user.avatar_url,
            is_active=updated_user.is_active,
            is_verified=updated_user.is_verified,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
        )

    def _extract_path_from_url(self, url: str) -> str:
        """Extract storage path from URL.

        Args:
            url: Full URL to the file

        Returns:
            Relative path for storage operations
        """
        # Remove base URL to get relative path
        # Assuming URL format: http://base/storage/path/to/file
        # This is a simple implementation - might need adjustment based on actual URL format
        from src.infrastructure.config import get_settings

        settings = get_settings()
        base_url = settings.storage_base_url.rstrip("/")
        
        if url.startswith(base_url):
            return url[len(base_url) + 1 :]  # +1 to skip the leading /
        
        # If URL doesn't match base, try to extract from common patterns
        if "/storage/" in url:
            return url.split("/storage/", 1)[1]
        
        # Fallback: return as-is (assuming it's already a path)
        return url


class DeleteAvatarUseCase:
    """Use case for deleting user avatar."""

    def __init__(
        self,
        user_repository: UserRepository,
        storage_service: StorageService,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            user_repository: User repository for data access
            storage_service: Storage service for file operations
        """
        self._user_repository = user_repository
        self._storage_service = storage_service

    async def execute(self, user_id: str) -> UserResponse:
        """Execute avatar deletion.

        Args:
            user_id: Current user ID

        Returns:
            Updated user profile response DTO

        Raises:
            EntityNotFoundException: If user not found
            StorageException: If storage operation fails
        """
        from uuid import UUID

        logger.info("Deleting avatar", user_id=user_id)

        user_uuid = UUID(user_id)
        user = await self._user_repository.get_by_id(user_uuid)

        if user is None:
            logger.warning("User not found for avatar deletion", user_id=user_id)
            raise EntityNotFoundException("User", user_id)

        if not user.avatar_url:
            # No avatar to delete, just return user
            logger.info("No avatar to delete", user_id=user_id)
            return UserResponse(
                id=user.id,
                email=user.email.value,
                name=user.name,
                avatar_url=user.avatar_url,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )

        # Delete file from storage
        # Extract path from URL
        upload_use_case = UploadAvatarUseCase(self._user_repository, self._storage_service)
        file_path = upload_use_case._extract_path_from_url(user.avatar_url)
        
        try:
            # Delete all sizes (assuming naming pattern)
            # Delete main file
            await self._storage_service.delete(file_path)
            
            # Try to delete other sizes (they might have _64x64, _128x128, _256x256 suffixes)
            path_obj = Path(file_path)
            base_name = path_obj.stem.rsplit("_", 1)[0]  # Remove size suffix if present
            extension = path_obj.suffix
            
            for size_config in ImageProcessingService.AVATAR_SIZES:
                size_file_path = f"{path_obj.parent}/{base_name}_{size_config.name}{extension}"
                try:
                    await self._storage_service.delete(size_file_path)
                except Exception:
                    # Ignore errors for individual size deletions
                    pass
                    
        except Exception as e:
            logger.warning("Failed to delete avatar file from storage", path=file_path, error=str(e))
            # Continue with clearing avatar_url even if file deletion fails

        # Clear avatar URL in database
        user.update_avatar(None)
        updated_user = await self._user_repository.update(user)

        logger.info("Avatar deleted", user_id=user_id)

        return UserResponse(
            id=updated_user.id,
            email=updated_user.email.value,
            name=updated_user.name,
            avatar_url=updated_user.avatar_url,
            is_active=updated_user.is_active,
            is_verified=updated_user.is_verified,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
        )

