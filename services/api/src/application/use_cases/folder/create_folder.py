"""Create folder use case."""

import structlog

from src.application.dtos.folder import CreateFolderRequest, FolderResponse
from src.domain.entities import Folder
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import FolderRepository, OrganizationRepository

logger = structlog.get_logger()


class CreateFolderUseCase:
    """Use case for creating a folder."""

    def __init__(
        self,
        folder_repository: FolderRepository,
        organization_repository: OrganizationRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            folder_repository: Folder repository
            organization_repository: Organization repository to verify organization exists
        """
        self._folder_repository = folder_repository
        self._organization_repository = organization_repository

    async def execute(self, request: CreateFolderRequest, creator_user_id: str) -> FolderResponse:
        """Execute folder creation.

        Args:
            request: Folder creation request
            creator_user_id: ID of the user creating the folder (for logging)

        Returns:
            Created folder response DTO

        Raises:
            EntityNotFoundException: If organization not found
            ConflictException: If folder name already exists in organization/parent
        """
        logger.info(
            "Creating folder",
            name=request.name,
            organization_id=str(request.organization_id),
            parent_id=str(request.parent_id) if request.parent_id else None,
            creator_user_id=creator_user_id,
        )

        # Verify organization exists
        organization = await self._organization_repository.get_by_id(request.organization_id)
        if organization is None:
            logger.warning(
                "Organization not found for folder creation",
                organization_id=str(request.organization_id),
            )
            raise EntityNotFoundException("Organization", str(request.organization_id))

        # Verify parent folder exists if provided
        if request.parent_id:
            parent_folder = await self._folder_repository.get_by_id(request.parent_id)
            if parent_folder is None:
                logger.warning(
                    "Parent folder not found for folder creation",
                    parent_id=str(request.parent_id),
                )
                raise EntityNotFoundException("Folder", str(request.parent_id))

            # Verify parent belongs to same organization
            if parent_folder.organization_id != request.organization_id:
                logger.warning(
                    "Parent folder belongs to different organization",
                    parent_id=str(request.parent_id),
                    parent_org_id=str(parent_folder.organization_id),
                    requested_org_id=str(request.organization_id),
                )
                raise EntityNotFoundException("Folder", str(request.parent_id))

        # Check for name conflict before creating
        if await self._folder_repository.exists_by_name(
            request.organization_id, request.name, request.parent_id
        ):
            logger.warning(
                "Folder name conflict",
                name=request.name,
                organization_id=str(request.organization_id),
                parent_id=str(request.parent_id) if request.parent_id else None,
            )
            raise ConflictException(
                f"Folder with name '{request.name}' already exists in this location",
                field="name",
            )

        # Create folder entity
        folder = Folder.create(
            organization_id=request.organization_id,
            name=request.name,
            parent_id=request.parent_id,
            position=request.position,
        )

        # Persist folder
        created_folder = await self._folder_repository.create(folder)

        logger.info(
            "Folder created successfully",
            folder_id=str(created_folder.id),
            name=created_folder.name,
        )

        return FolderResponse(
            id=created_folder.id,
            organization_id=created_folder.organization_id,
            name=created_folder.name,
            parent_id=created_folder.parent_id,
            position=created_folder.position,
            created_at=created_folder.created_at,
            updated_at=created_folder.updated_at,
        )
