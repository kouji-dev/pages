"""Delete attachment use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import AttachmentRepository, ProjectRepository
from src.domain.services import StorageService

logger = structlog.get_logger()


class DeleteAttachmentUseCase:
    """Use case for deleting an attachment."""

    def __init__(
        self,
        attachment_repository: AttachmentRepository,
        project_repository: ProjectRepository,
        storage_service: StorageService,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            attachment_repository: Attachment repository for data access
            project_repository: Project repository for permission check
            storage_service: Storage service for deleting files
        """
        self._attachment_repository = attachment_repository
        self._project_repository = project_repository
        self._storage_service = storage_service

    async def execute(
        self, attachment_id: str, user_id: UUID, is_project_admin: bool = False
    ) -> None:
        """Execute delete attachment.

        Args:
            attachment_id: Attachment ID
            user_id: ID of the user deleting the attachment
            is_project_admin: Whether the user is a project admin

        Raises:
            EntityNotFoundException: If attachment not found
            ValidationException: If user is not authorized to delete
        """
        logger.info("Deleting attachment", attachment_id=attachment_id)

        attachment_uuid = UUID(attachment_id)
        attachment = await self._attachment_repository.get_by_id(attachment_uuid)

        if attachment is None:
            logger.warning("Attachment not found for deletion", attachment_id=attachment_id)
            raise EntityNotFoundException("Attachment", attachment_id)

        # Check permission: uploader or project admin
        if attachment.uploaded_by != user_id and not is_project_admin:
            logger.warning(
                "User not authorized to delete attachment",
                attachment_id=attachment_id,
                user_id=str(user_id),
                uploader_id=str(attachment.uploaded_by),
            )
            raise ValidationException(
                "Only the uploader or project admin can delete the attachment",
                field="user_id",
            )

        # Delete file from storage
        try:
            await self._storage_service.delete(attachment.storage_path)
            logger.info("File deleted from storage", storage_path=attachment.storage_path)
        except Exception as e:
            logger.warning(
                "Failed to delete file from storage",
                storage_path=attachment.storage_path,
                error=str(e),
            )
            # Continue with database deletion even if storage deletion fails

        # Delete from database
        await self._attachment_repository.delete(attachment_uuid)

        logger.info("Attachment deleted", attachment_id=attachment_id)

