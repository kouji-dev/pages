"""Create project use case."""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.project import CreateProjectRequest, ProjectResponse
from src.domain.entities import Project
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import OrganizationRepository, ProjectRepository, UserRepository
from src.infrastructure.database.models import ProjectMemberModel

logger = structlog.get_logger()


class CreateProjectUseCase:
    """Use case for creating a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        organization_repository: OrganizationRepository,
        user_repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            project_repository: Project repository
            organization_repository: Organization repository to verify organization exists
            user_repository: User repository to verify creator exists
            session: Database session for creating project member and counting issues
        """
        self._project_repository = project_repository
        self._organization_repository = organization_repository
        self._user_repository = user_repository
        self._session = session

    async def execute(self, request: CreateProjectRequest, creator_user_id: str) -> ProjectResponse:
        """Execute project creation.

        Args:
            request: Project creation request
            creator_user_id: ID of the user creating the project

        Returns:
            Created project response DTO with member and issue counts

        Raises:
            EntityNotFoundException: If organization or creator user not found
            ConflictException: If project key already exists in organization
        """
        logger.info(
            "Creating project",
            name=request.name,
            key=request.key,
            organization_id=str(request.organization_id),
            creator_user_id=creator_user_id,
        )

        # Verify organization exists
        organization = await self._organization_repository.get_by_id(request.organization_id)
        if organization is None:
            logger.warning(
                "Organization not found for project creation",
                organization_id=str(request.organization_id),
            )
            raise EntityNotFoundException("Organization", str(request.organization_id))

        # Verify creator exists
        creator_uuid = UUID(creator_user_id)
        creator = await self._user_repository.get_by_id(creator_uuid)
        if creator is None:
            logger.warning("Creator user not found", creator_user_id=creator_user_id)
            raise EntityNotFoundException("User", creator_user_id)

        # Create project entity
        project = Project.create(
            organization_id=request.organization_id,
            name=request.name,
            key=request.key,
            description=request.description,
        )

        # Persist project
        created_project = await self._project_repository.create(project)

        # Create project member with admin role
        project_member = ProjectMemberModel(
            project_id=created_project.id,
            user_id=creator_uuid,
            role="admin",
        )
        self._session.add(project_member)
        await self._session.flush()

        # Count members
        result = await self._session.execute(
            select(func.count())
            .select_from(ProjectMemberModel)
            .where(ProjectMemberModel.project_id == created_project.id)
        )
        member_count: int = result.scalar_one()

        # Count issues (will be 0 for new project)
        from src.infrastructure.database.models import IssueModel

        result = await self._session.execute(
            select(func.count())
            .select_from(IssueModel)
            .where(IssueModel.project_id == created_project.id)
        )
        issue_count: int = result.scalar_one()

        logger.info(
            "Project created successfully",
            project_id=str(created_project.id),
            key=created_project.key,
        )

        return ProjectResponse(
            id=created_project.id,
            organization_id=created_project.organization_id,
            name=created_project.name,
            key=created_project.key,
            description=created_project.description,
            settings=created_project.settings,
            member_count=member_count,
            issue_count=issue_count,
            created_at=created_project.created_at,
            updated_at=created_project.updated_at,
        )
