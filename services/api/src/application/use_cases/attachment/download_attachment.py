"""Download attachment use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import AttachmentRepository
from src.domain.services import StorageService

logger = structlog.get_logger()


class DownloadAttachmentUseCase:
    """Use case for downloading an attachment file."""

    def __init__(
        self,
        attachment_repository: AttachmentRepository,
        storage_service: StorageService,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            attachment_repository: Attachment repository
            storage_service: Storage service for retrieving files
        """
        self._attachment_repository = attachment_repository
        self._storage_service = storage_service

    async def execute(self, attachment_id: str) -> tuple[bytes, str, str]:
        """Execute download attachment.

        Args:
            attachment_id: Attachment ID

        Returns:
            Tuple of (file_content, mime_type, original_filename)

        Raises:
            EntityNotFoundException: If attachment not found
        """
        logger.info("Downloading attachment", attachment_id=attachment_id)

        attachment_uuid = UUID(attachment_id)
        attachment = await self._attachment_repository.get_by_id(attachment_uuid)

        if attachment is None:
            logger.warning("Attachment not found for download", attachment_id=attachment_id)
            raise EntityNotFoundException("Attachment", attachment_id)

        # Get file from storage
        try:
            file_content = await self._storage_service.get_file(attachment.storage_path)
        except Exception as e:
            logger.error(
                "Failed to retrieve file from storage",
                storage_path=attachment.storage_path,
                error=str(e),
            )
            raise EntityNotFoundException("Attachment file", attachment.storage_path) from e

        logger.info("Attachment downloaded", attachment_id=attachment_id)

        return file_content, attachment.mime_type, attachment.original_name
