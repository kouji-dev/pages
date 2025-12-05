"""Upload attachment use case."""

import hashlib
from pathlib import Path
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.attachment import UploadAttachmentResponse
from src.application.utils.file_validation import (
    generate_unique_filename,
    validate_file_size,
    validate_file_type,
)
from src.domain.entities import Attachment
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import AttachmentRepository, IssueRepository, UserRepository
from src.domain.services import StorageService
from src.infrastructure.database.models import UserModel

logger = structlog.get_logger()


class UploadAttachmentUseCase:
    """Use case for uploading a file attachment to an issue."""

    def __init__(
        self,
        attachment_repository: AttachmentRepository,
        issue_repository: IssueRepository,
        user_repository: UserRepository,
        storage_service: StorageService,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            attachment_repository: Attachment repository
            issue_repository: Issue repository to verify issue exists
            user_repository: User repository to verify user exists
            storage_service: Storage service for file operations
            session: Database session for loading user details
        """
        self._attachment_repository = attachment_repository
        self._issue_repository = issue_repository
        self._user_repository = user_repository
        self._storage_service = storage_service
        self._session = session

    async def execute(
        self,
        issue_id: str,
        file_content: bytes,
        original_filename: str,
        mime_type: str,
        user_id: str,
    ) -> UploadAttachmentResponse:
        """Execute file upload.

        Args:
            issue_id: Issue ID
            file_content: File content as bytes
            original_filename: Original filename from user
            mime_type: MIME type of the file
            user_id: ID of the user uploading the file

        Returns:
            Upload attachment response DTO

        Raises:
            EntityNotFoundException: If issue or user not found
            ValidationException: If file type or size is invalid
        """
        logger.info(
            "Uploading attachment",
            issue_id=issue_id,
            filename=original_filename,
            mime_type=mime_type,
            file_size=len(file_content),
            user_id=user_id,
        )

        # Validate file type
        if not validate_file_type(mime_type):
            logger.warning("Invalid file type", mime_type=mime_type)
            raise ValidationException(
                f"File type '{mime_type}' is not allowed", field="mime_type"
            )

        # Validate file size
        file_size = len(file_content)
        if not validate_file_size(file_size):
            logger.warning("File size exceeds limit", file_size=file_size)
            raise ValidationException(
                f"File size ({file_size} bytes) exceeds maximum allowed size (10MB)",
                field="file_size",
            )

        # Verify issue exists
        issue_uuid = UUID(issue_id)
        issue = await self._issue_repository.get_by_id(issue_uuid)
        if issue is None:
            logger.warning("Issue not found for attachment upload", issue_id=issue_id)
            raise EntityNotFoundException("Issue", issue_id)

        # Verify user exists
        user_uuid = UUID(user_id)
        user = await self._user_repository.get_by_id(user_uuid)
        if user is None:
            logger.warning("User not found", user_id=user_id)
            raise EntityNotFoundException("User", user_id)

        # Generate a temporary ID for filename generation
        from uuid import uuid4 as generate_uuid

        temp_id = generate_uuid()

        # Generate unique filename
        unique_filename = generate_unique_filename(original_filename, temp_id)

        # Create temporary storage path (will be updated after saving)
        temp_storage_path = f"attachments/{temp_id}/{unique_filename}"

        # Create attachment entity with generated filename
        attachment = Attachment.create(
            entity_type="issue",
            entity_id=issue_uuid,
            file_name=unique_filename,
            original_name=original_filename,
            file_size=file_size,
            mime_type=mime_type,
            storage_path=temp_storage_path,  # Temporary, will be updated
            storage_type="local",
            uploaded_by=user_uuid,
        )

        # Update storage path with actual attachment ID
        storage_path = f"attachments/{attachment.id}/{unique_filename}"
        try:
            await self._storage_service.save(
                file_content=file_content,
                file_path=storage_path,
                content_type=mime_type,
            )
        except Exception as e:
            logger.error("Failed to save file to storage", error=str(e))
            raise ValidationException(f"Failed to save file: {str(e)}", field="file") from e

        # Update attachment with storage path
        attachment.storage_path = storage_path

        # Persist attachment
        created_attachment = await self._attachment_repository.create(attachment)

        # Load user details for response
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_uuid)
        )
        user_model = result.scalar_one()

        # Get download URL
        download_url = await self._storage_service.get_url(storage_path)

        logger.info(
            "Attachment uploaded successfully",
            attachment_id=str(created_attachment.id),
            issue_id=issue_id,
        )

        # Convert to response DTO
        return UploadAttachmentResponse(
            id=created_attachment.id,
            entity_type=created_attachment.entity_type,
            entity_id=created_attachment.entity_id,
            file_name=created_attachment.file_name,
            original_name=created_attachment.original_name,
            file_size=created_attachment.file_size,
            mime_type=created_attachment.mime_type,
            storage_path=created_attachment.storage_path,
            storage_type=created_attachment.storage_type,
            thumbnail_path=created_attachment.thumbnail_path,
            uploaded_by=created_attachment.uploaded_by,
            uploader_name=user_model.name,
            uploader_email=user_model.email,
            download_url=download_url,
            created_at=created_attachment.created_at,
            updated_at=created_attachment.updated_at,
        )

