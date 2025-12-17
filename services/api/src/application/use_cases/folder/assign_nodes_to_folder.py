"""Assign nodes to folder use case."""

from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.folder import AssignNodesToFolderRequest
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import FolderRepository, ProjectRepository, SpaceRepository
from src.infrastructure.database.models import ProjectModel, SpaceModel

logger = structlog.get_logger()


class AssignNodesToFolderUseCase:
    """Use case for assigning nodes (projects/spaces) to a folder."""

    def __init__(
        self,
        folder_repository: FolderRepository,
        project_repository: ProjectRepository,
        space_repository: SpaceRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            folder_repository: Folder repository
            project_repository: Project repository
            space_repository: Space repository
            session: Database session for updating folder_id
        """
        self._folder_repository = folder_repository
        self._project_repository = project_repository
        self._space_repository = space_repository
        self._session = session

    async def execute(
        self, folder_id: str, request: AssignNodesToFolderRequest
    ) -> None:
        """Execute node assignment to folder.

        Args:
            folder_id: Folder UUID
            request: Assignment request with node IDs

        Raises:
            EntityNotFoundException: If folder or any node not found
        """
        logger.info(
            "Assigning nodes to folder",
            folder_id=folder_id,
            node_count=len(request.node_ids),
        )

        folder_uuid = UUID(folder_id)
        folder = await self._folder_repository.get_by_id(folder_uuid)

        if folder is None:
            logger.warning("Folder not found for node assignment", folder_id=folder_id)
            raise EntityNotFoundException("Folder", folder_id)

        # Process each node ID
        for node_id in request.node_ids:
            node_uuid = UUID(str(node_id))

            # Try to find as project first
            project = await self._project_repository.get_by_id(node_uuid)
            if project:
                # Verify project belongs to same organization
                if project.organization_id != folder.organization_id:
                    logger.warning(
                        "Project belongs to different organization",
                        project_id=str(node_id),
                        project_org_id=str(project.organization_id),
                        folder_org_id=str(folder.organization_id),
                    )
                    raise EntityNotFoundException("Project", str(node_id))

                # Update project's folder_id
                from sqlalchemy import select

                result = await self._session.execute(
                    select(ProjectModel).where(ProjectModel.id == node_uuid)
                )
                project_model = result.scalar_one_or_none()
                if project_model:
                    project_model.folder_id = folder_uuid
                    await self._session.flush()
                continue

            # Try to find as space
            space = await self._space_repository.get_by_id(node_uuid)
            if space:
                # Verify space belongs to same organization
                if space.organization_id != folder.organization_id:
                    logger.warning(
                        "Space belongs to different organization",
                        space_id=str(node_id),
                        space_org_id=str(space.organization_id),
                        folder_org_id=str(folder.organization_id),
                    )
                    raise EntityNotFoundException("Space", str(node_id))

                # Update space's folder_id
                from sqlalchemy import select

                result = await self._session.execute(
                    select(SpaceModel).where(SpaceModel.id == node_uuid)
                )
                space_model = result.scalar_one_or_none()
                if space_model:
                    space_model.folder_id = folder_uuid
                    await self._session.flush()
                continue

            # Node not found as project or space
            logger.warning("Node not found", node_id=str(node_id))
            raise EntityNotFoundException("Node", str(node_id))

        logger.info("Nodes assigned to folder successfully", folder_id=folder_id)

