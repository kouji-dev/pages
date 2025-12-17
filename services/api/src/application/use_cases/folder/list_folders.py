"""List folders use case."""

from uuid import UUID

import structlog

from src.application.dtos.folder import FolderListResponse, FolderListItemResponse
from src.domain.repositories import FolderRepository

logger = structlog.get_logger()


class ListFoldersUseCase:
    """Use case for listing folders in an organization."""

    def __init__(self, folder_repository: FolderRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            folder_repository: Folder repository
        """
        self._folder_repository = folder_repository

    async def execute(
        self,
        organization_id: str,
        parent_id: str | None = None,
        include_deleted: bool = False,
    ) -> FolderListResponse:
        """Execute list folders.

        Args:
            organization_id: Organization UUID
            parent_id: Optional parent folder UUID to filter by (None for root folders)
            include_deleted: Whether to include soft-deleted folders

        Returns:
            Folder list response DTO
        """
        org_uuid = UUID(organization_id)
        parent_uuid = UUID(parent_id) if parent_id else None

        logger.info(
            "Listing folders",
            organization_id=organization_id,
            parent_id=parent_id,
            include_deleted=include_deleted,
        )

        # If parent_id is not specified, get all folders (not just root folders)
        # We need to pass None explicitly to get all folders regardless of parent
        folders = await self._folder_repository.get_all(
            organization_id=org_uuid,
            parent_id=parent_uuid,  # None means all folders, specific UUID means children of that folder
            skip=0,
            limit=1000,  # Large limit for folders (usually not many)
            include_deleted=include_deleted,
        )

        total = await self._folder_repository.count(
            organization_id=org_uuid,
            parent_id=parent_uuid,
            include_deleted=include_deleted,
        )

        folder_responses = [
            FolderListItemResponse(
                id=folder.id,
                organization_id=folder.organization_id,
                name=folder.name,
                parent_id=folder.parent_id,
                position=folder.position,
                created_at=folder.created_at,
                updated_at=folder.updated_at,
            )
            for folder in folders
        ]

        logger.info("Folders listed", count=len(folder_responses), total=total)

        return FolderListResponse(folders=folder_responses, total=total)
