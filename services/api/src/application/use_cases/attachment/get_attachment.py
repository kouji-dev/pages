"""Get attachment use case."""

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.attachment import AttachmentResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import AttachmentRepository
from src.domain.services import StorageService
from src.infrastructure.database.models import UserModel

logger = structlog.get_logger()


class GetAttachmentUseCase:
    """Use case for retrieving an attachment by ID."""

    def __init__(
        self,
        attachment_repository: AttachmentRepository,
        storage_service: StorageService,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            attachment_repository: Attachment repository
            storage_service: Storage service for getting download URL
            session: Database session for loading user details
        """
        self._attachment_repository = attachment_repository
        self._storage_service = storage_service
        self._session = session

    async def execute(self, attachment_id: str) -> AttachmentResponse:
        """Execute get attachment.

        Args:
            attachment_id: Attachment ID

        Returns:
            Attachment response DTO

        Raises:
            EntityNotFoundException: If attachment not found
        """
        logger.info("Getting attachment", attachment_id=attachment_id)

        attachment_uuid = UUID(attachment_id)
        attachment = await self._attachment_repository.get_by_id(attachment_uuid)

        if attachment is None:
            logger.warning("Attachment not found", attachment_id=attachment_id)
            raise EntityNotFoundException("Attachment", attachment_id)

        # Load user details if uploaded_by is set
        uploader_name = None
        uploader_email = None
        if attachment.uploaded_by:
            result = await self._session.execute(
                select(UserModel).where(UserModel.id == attachment.uploaded_by)
            )
            user_model = result.scalar_one_or_none()
            if user_model:
                uploader_name = user_model.name
                uploader_email = user_model.email

        # Get download URL
        download_url = await self._storage_service.get_url(attachment.storage_path)

        logger.info("Attachment retrieved", attachment_id=attachment_id)

        # Convert to response DTO
        return AttachmentResponse(
            id=attachment.id,
            entity_type=attachment.entity_type,
            entity_id=attachment.entity_id,
            file_name=attachment.file_name,
            original_name=attachment.original_name,
            file_size=attachment.file_size,
            mime_type=attachment.mime_type,
            storage_path=attachment.storage_path,
            storage_type=attachment.storage_type,
            thumbnail_path=attachment.thumbnail_path,
            uploaded_by=attachment.uploaded_by,
            uploader_name=uploader_name,
            uploader_email=uploader_email,
            download_url=download_url,
            created_at=attachment.created_at,
            updated_at=attachment.updated_at,
        )

