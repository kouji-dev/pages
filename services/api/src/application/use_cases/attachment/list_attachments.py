"""List attachments use case."""

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.attachment import AttachmentListItemResponse, AttachmentListResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import AttachmentRepository, IssueRepository
from src.domain.services import StorageService
from src.infrastructure.database.models import UserModel

logger = structlog.get_logger()


class ListAttachmentsUseCase:
    """Use case for listing attachments for an issue."""

    def __init__(
        self,
        attachment_repository: AttachmentRepository,
        issue_repository: IssueRepository,
        storage_service: StorageService,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            attachment_repository: Attachment repository
            issue_repository: Issue repository to verify issue exists
            storage_service: Storage service for getting download URLs
            session: Database session for loading user details
        """
        self._attachment_repository = attachment_repository
        self._issue_repository = issue_repository
        self._storage_service = storage_service
        self._session = session

    async def execute(self, issue_id: str) -> AttachmentListResponse:
        """Execute list attachments for issue.

        Args:
            issue_id: Issue ID

        Returns:
            List of attachments response DTO

        Raises:
            EntityNotFoundException: If issue not found
        """
        logger.info("Listing attachments for issue", issue_id=issue_id)

        # Verify issue exists
        issue_uuid = UUID(issue_id)
        issue = await self._issue_repository.get_by_id(issue_uuid)
        if issue is None:
            logger.warning("Issue not found", issue_id=issue_id)
            raise EntityNotFoundException("Issue", issue_id)

        # Get attachments
        attachments = await self._attachment_repository.get_by_entity_id(
            entity_type="issue",
            entity_id=issue_uuid,
        )

        # Load user details for attachments
        user_ids = {att.uploaded_by for att in attachments if att.uploaded_by}
        users_map = {}
        if user_ids:
            result = await self._session.execute(
                select(UserModel).where(UserModel.id.in_(user_ids))
            )
            users = result.scalars().all()
            users_map = {user.id: user for user in users}

        # Convert to response DTOs
        attachment_responses = []
        for attachment in attachments:
            user = users_map.get(attachment.uploaded_by) if attachment.uploaded_by else None
            download_url = await self._storage_service.get_url(attachment.storage_path)

            attachment_responses.append(
                AttachmentListItemResponse(
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
                    uploader_name=user.name if user else None,
                    uploader_email=user.email if user else None,
                    download_url=download_url,
                    created_at=attachment.created_at,
                    updated_at=attachment.updated_at,
                )
            )

        logger.info(
            "Attachments listed successfully",
            issue_id=issue_id,
            count=len(attachment_responses),
        )

        return AttachmentListResponse(
            attachments=attachment_responses,
            total=len(attachment_responses),
        )
