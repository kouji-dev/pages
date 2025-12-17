"""Update folder use case."""

from uuid import UUID

import structlog

from src.application.dtos.folder import FolderResponse, UpdateFolderRequest
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import FolderRepository

logger = structlog.get_logger()


class UpdateFolderUseCase:
    """Use case for updating a folder."""

    def __init__(self, folder_repository: FolderRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            folder_repository: Folder repository
        """
        self._folder_repository = folder_repository

    async def execute(
        self, folder_id: str, request: UpdateFolderRequest
    ) -> FolderResponse:
        """Execute folder update.

        Args:
            folder_id: Folder UUID
            request: Folder update request

        Returns:
            Updated folder response DTO

        Raises:
            EntityNotFoundException: If folder not found
            ConflictException: If folder name conflicts with another folder
        """
        logger.info("Updating folder", folder_id=folder_id, updates=request.model_dump())

        folder_uuid = UUID(folder_id)
        folder = await self._folder_repository.get_by_id(folder_uuid)

        if folder is None:
            logger.warning("Folder not found for update", folder_id=folder_id)
            raise EntityNotFoundException("Folder", folder_id)

        # Verify parent folder exists if provided
        if request.parent_id is not None:
            if request.parent_id == folder.id:
                from src.domain.exceptions import ValidationException

                raise ValidationException(
                    "Folder cannot be its own parent", field="parent_id"
                )

            parent_folder = await self._folder_repository.get_by_id(request.parent_id)
            if parent_folder is None:
                logger.warning(
                    "Parent folder not found for folder update",
                    parent_id=str(request.parent_id),
                )
                raise EntityNotFoundException("Folder", str(request.parent_id))

            # Verify parent belongs to same organization
            if parent_folder.organization_id != folder.organization_id:
                logger.warning(
                    "Parent folder belongs to different organization",
                    parent_id=str(request.parent_id),
                    parent_org_id=str(parent_folder.organization_id),
                    folder_org_id=str(folder.organization_id),
                )
                raise EntityNotFoundException("Folder", str(request.parent_id))

        # Update folder using domain methods
        if request.name is not None:
            folder.update_name(request.name)

        if request.parent_id is not None:
            folder.update_parent(request.parent_id)

        if request.position is not None:
            folder.update_position(request.position)

        # Persist changes
        updated_folder = await self._folder_repository.update(folder)

        logger.info("Folder updated successfully", folder_id=folder_id)

        return FolderResponse(
            id=updated_folder.id,
            organization_id=updated_folder.organization_id,
            name=updated_folder.name,
            parent_id=updated_folder.parent_id,
            position=updated_folder.position,
            created_at=updated_folder.created_at,
            updated_at=updated_folder.updated_at,
        )

