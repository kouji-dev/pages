"""Get project use case."""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.project import ProjectResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import ProjectRepository
from src.infrastructure.database.models import IssueModel, ProjectMemberModel

logger = structlog.get_logger()


class GetProjectUseCase:
    """Use case for retrieving a project."""

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

    async def execute(self, project_id: str) -> ProjectResponse:
        """Execute get project.

        Args:
            project_id: Project ID

        Returns:
            Project response DTO with member and issue counts

        Raises:
            EntityNotFoundException: If project not found
        """
        logger.info("Getting project", project_id=project_id)

        project_uuid = UUID(project_id)
        project = await self._project_repository.get_by_id(project_uuid)

        if project is None:
            logger.warning("Project not found", project_id=project_id)
            raise EntityNotFoundException("Project", project_id)

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

        return ProjectResponse(
            id=project.id,
            organization_id=project.organization_id,
            name=project.name,
            key=project.key,
            description=project.description,
            settings=project.settings,
            member_count=member_count,
            issue_count=issue_count,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
