"""List folders and nodes use case."""

from uuid import UUID

import structlog

from src.application.dtos.unified import (
    ITEM_TYPE_FOLDER,
    ITEM_TYPE_PROJECT,
    ITEM_TYPE_SPACE,
    DTOItemFolder,
    DTOItemProject,
    DTOItemSpace,
    DTOResponseFolder,
    DTOResponseProject,
    DTOResponseSpace,
    UnifiedListResponse,
)
from src.domain.repositories import FolderRepository, ProjectRepository, SpaceRepository

logger = structlog.get_logger()


class ListFoldersAndNodesUseCase:
    """Use case for listing folders and nodes (projects + spaces) in an organization."""

    def __init__(
        self,
        folder_repository: FolderRepository,
        project_repository: ProjectRepository,
        space_repository: SpaceRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            folder_repository: Folder repository (port)
            project_repository: Project repository (port)
            space_repository: Space repository (port)
        """
        self._folder_repository = folder_repository
        self._project_repository = project_repository
        self._space_repository = space_repository

    async def execute(
        self,
        organization_id: str,
        folder_id: str | None = None,
        parent_id: str | None = None,
        include_empty_folders: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> UnifiedListResponse:
        """Execute list folders and nodes.

        Args:
            organization_id: Organization UUID
            folder_id: Optional folder UUID to filter nodes by
            parent_id: Optional parent folder UUID to filter folders by
            include_empty_folders: Whether to include folders with no nodes
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Unified list response DTO with folders and nodes
        """
        org_uuid = UUID(organization_id)
        folder_uuid = UUID(folder_id) if folder_id else None
        parent_uuid = UUID(parent_id) if parent_id else None

        logger.info(
            "Listing folders and nodes",
            organization_id=organization_id,
            folder_id=folder_id,
            parent_id=parent_id,
            include_empty_folders=include_empty_folders,
            skip=skip,
            limit=limit,
        )

        # Get all folders (needed for filtering empty ones)
        # Use a large limit to get all folders, pagination will be applied later
        folders = await self._folder_repository.get_all(
            organization_id=org_uuid,
            parent_id=parent_uuid,
            skip=0,
            limit=10000,  # Large limit to get all folders for filtering
            include_deleted=False,
        )

        # Get all projects and spaces (needed for filtering empty folders)
        # Use a large limit, pagination will be applied after combining
        projects = await self._project_repository.get_all(
            organization_id=org_uuid,
            folder_id=folder_uuid,
            skip=0,
            limit=10000,  # Large limit to get all for filtering empty folders
            include_deleted=False,
        )

        spaces = await self._space_repository.get_all(
            organization_id=org_uuid,
            folder_id=folder_uuid,
            skip=0,
            limit=10000,  # Large limit to get all for filtering empty folders
            include_deleted=False,
        )

        # Filter empty folders if needed
        if not include_empty_folders:
            # Create a set of folder IDs that have nodes
            folders_with_nodes = set()
            for project in projects:
                if project.folder_id:
                    folders_with_nodes.add(project.folder_id)
            for space in spaces:
                if space.folder_id:
                    folders_with_nodes.add(space.folder_id)

            # Filter folders to only include those with nodes
            folders = [f for f in folders if f.id in folders_with_nodes]

        # Transform folders to DTOs
        folder_items = []
        for folder in folders:
            folder_items.append(
                DTOItemFolder(
                    type=ITEM_TYPE_FOLDER,
                    id=folder.id,
                    organization_id=folder.organization_id,
                    position=folder.position,
                    details=DTOResponseFolder(name=folder.name),
                )
            )

        # Transform projects to DTOs
        project_items = []
        for project in projects:
            project_items.append(
                DTOItemProject(
                    type=ITEM_TYPE_PROJECT,
                    id=project.id,
                    organization_id=project.organization_id,
                    details=DTOResponseProject(
                        name=project.name,
                        key=project.key,
                        description=project.description,
                        folder_id=project.folder_id,
                    ),
                )
            )

        # Transform spaces to DTOs
        space_items = []
        for space in spaces:
            space_items.append(
                DTOItemSpace(
                    type=ITEM_TYPE_SPACE,
                    id=space.id,
                    organization_id=space.organization_id,
                    details=DTOResponseSpace(
                        name=space.name,
                        key=space.key,
                        description=space.description,
                        folder_id=space.folder_id,
                    ),
                )
            )

        # Combine all items
        all_items: list[DTOItemFolder | DTOItemProject | DTOItemSpace] = []
        all_items.extend(folder_items)
        all_items.extend(project_items)
        all_items.extend(space_items)

        # Apply pagination
        total_items = len(all_items)
        paginated_items = all_items[skip : skip + limit]

        folders_count = len(folder_items)
        nodes_count = len(project_items) + len(space_items)

        logger.info(
            "Folders and nodes listed",
            total=total_items,
            folders_count=folders_count,
            nodes_count=nodes_count,
            organization_id=organization_id,
        )

        return UnifiedListResponse(
            items=paginated_items,
            folders_count=folders_count,
            nodes_count=nodes_count,
            total=total_items,
        )
