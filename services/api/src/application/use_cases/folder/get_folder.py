"""Get folder use case."""

from uuid import UUID

import structlog

from src.application.dtos.folder import FolderResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import FolderRepository

logger = structlog.get_logger()


class GetFolderUseCase:
    """Use case for getting a folder by ID."""

    def __init__(self, folder_repository: FolderRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            folder_repository: Folder repository
        """
        self._folder_repository = folder_repository

    async def execute(self, folder_id: str) -> FolderResponse:
        """Execute get folder.

        Args:
            folder_id: Folder UUID

        Returns:
            Folder response DTO

        Raises:
            EntityNotFoundException: If folder not found
        """
        logger.info("Getting folder", folder_id=folder_id)

        folder_uuid = UUID(folder_id)
        folder = await self._folder_repository.get_by_id(folder_uuid)

        if folder is None:
            logger.warning("Folder not found", folder_id=folder_id)
            raise EntityNotFoundException("Folder", folder_id)

        logger.info("Folder retrieved", folder_id=folder_id, name=folder.name)

        return FolderResponse(
            id=folder.id,
            organization_id=folder.organization_id,
            name=folder.name,
            parent_id=folder.parent_id,
            position=folder.position,
            created_at=folder.created_at,
            updated_at=folder.updated_at,
        )

