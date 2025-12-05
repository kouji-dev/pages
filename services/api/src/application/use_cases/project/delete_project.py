"""Delete project use case."""

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import ProjectRepository

logger = structlog.get_logger()


class DeleteProjectUseCase:
    """Use case for deleting a project."""

    def __init__(self, project_repository: ProjectRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            project_repository: Project repository
        """
        self._project_repository = project_repository

    async def execute(self, project_id: str) -> None:
        """Execute delete project (soft delete).

        Args:
            project_id: Project ID

        Raises:
            EntityNotFoundException: If project not found
        """
        from uuid import UUID

        logger.info("Deleting project", project_id=project_id)

        project_uuid = UUID(project_id)
        project = await self._project_repository.get_by_id(project_uuid)

        if project is None:
            logger.warning("Project not found for deletion", project_id=project_id)
            raise EntityNotFoundException("Project", project_id)

        # Soft delete
        project.delete()
        await self._project_repository.update(project)

        logger.info("Project deleted", project_id=project_id)

