"""Update project use case."""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.project import ProjectResponse, UpdateProjectRequest
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import ProjectRepository
from src.infrastructure.database.models import IssueModel, ProjectMemberModel

logger = structlog.get_logger()


class UpdateProjectUseCase:
    """Use case for updating a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            project_repository: Project repository
            session: Database session for counting members and issues
        """
        self._project_repository = project_repository
        self._session = session

    async def execute(self, project_id: str, request: UpdateProjectRequest) -> ProjectResponse:
        """Execute update project.

        Args:
            project_id: Project ID
            request: Project update request

        Returns:
            Updated project response DTO with member and issue counts

        Raises:
            EntityNotFoundException: If project not found
            ConflictException: If project key conflicts with another project
        """
        logger.info("Updating project", project_id=project_id)

        project_uuid = UUID(project_id)
        project = await self._project_repository.get_by_id(project_uuid)

        if project is None:
            logger.warning("Project not found for update", project_id=project_id)
            raise EntityNotFoundException("Project", project_id)

        # Update fields if provided
        if request.name is not None:
            project.update_name(request.name, regenerate_key=False)

        if request.key is not None:
            project.update_key(request.key)

        if request.description is not None:
            project.update_description(request.description)

        # Persist changes
        updated_project = await self._project_repository.update(project)

        # Count members
        result = await self._session.execute(
            select(func.count())
            .select_from(ProjectMemberModel)
            .where(ProjectMemberModel.project_id == project_uuid)
        )
        member_count: int = result.scalar_one()

        # Count issues
        result = await self._session.execute(
            select(func.count())
            .select_from(IssueModel)
            .where(IssueModel.project_id == project_uuid)
        )
        issue_count: int = result.scalar_one()

        logger.info("Project updated", project_id=project_id)

        return ProjectResponse(
            id=updated_project.id,
            organization_id=updated_project.organization_id,
            name=updated_project.name,
            key=updated_project.key,
            description=updated_project.description,
            settings=updated_project.settings,
            member_count=member_count,
            issue_count=issue_count,
            created_at=updated_project.created_at,
            updated_at=updated_project.updated_at,
        )
