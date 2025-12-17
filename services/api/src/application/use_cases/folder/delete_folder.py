"""Delete folder use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import FolderRepository

logger = structlog.get_logger()


class DeleteFolderUseCase:
    """Use case for deleting a folder."""

    def __init__(self, folder_repository: FolderRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            folder_repository: Folder repository
        """
        self._folder_repository = folder_repository

    async def execute(self, folder_id: str) -> None:
        """Execute folder deletion.

        Args:
            folder_id: Folder UUID

        Raises:
            EntityNotFoundException: If folder not found
        """
        logger.info("Deleting folder", folder_id=folder_id)

        folder_uuid = UUID(folder_id)
        folder = await self._folder_repository.get_by_id(folder_uuid)

        if folder is None:
            logger.warning("Folder not found for deletion", folder_id=folder_id)
            raise EntityNotFoundException("Folder", folder_id)

        # Soft delete using domain method
        folder.delete()

        # Persist deletion
        await self._folder_repository.update(folder)

        logger.info("Folder deleted successfully", folder_id=folder_id)

