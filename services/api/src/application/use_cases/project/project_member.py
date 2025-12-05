"""Project member management use cases."""

from math import ceil
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.project_member import (
    AddProjectMemberRequest,
    ProjectMemberListResponse,
    ProjectMemberResponse,
    UpdateProjectMemberRoleRequest,
)
from src.domain.exceptions import ConflictException, EntityNotFoundException, ValidationException
from src.domain.repositories import ProjectRepository, UserRepository
from src.domain.value_objects import Role

logger = structlog.get_logger()


class AddProjectMemberUseCase:
    """Use case for adding a member to a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        user_repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            project_repository: Project repository
            user_repository: User repository
            session: Database session
        """
        self._project_repository = project_repository
        self._user_repository = user_repository
        self._session = session

    async def execute(
        self, project_id: str, request: AddProjectMemberRequest
    ) -> ProjectMemberResponse:
        """Execute add member to project.

        Args:
            project_id: Project ID
            request: Add member request

        Returns:
            Added member response DTO

        Raises:
            EntityNotFoundException: If project or user not found
            ConflictException: If user is already a member
            ValidationException: If role is invalid
        """
        from src.infrastructure.database.models import ProjectMemberModel, UserModel

        logger.info(
            "Adding member to project",
            project_id=project_id,
            user_id=str(request.user_id),
            role=request.role,
        )

        # Validate role
        if not Role.is_valid(request.role):
            raise ValidationException(
                f"Invalid role: {request.role}. Must be one of: admin, member, viewer"
            )

        # Verify project exists
        project_uuid = UUID(project_id)
        project = await self._project_repository.get_by_id(project_uuid)

        if project is None:
            logger.warning("Project not found", project_id=project_id)
            raise EntityNotFoundException("Project", project_id)

        # Verify user exists
        user = await self._user_repository.get_by_id(request.user_id)

        if user is None:
            logger.warning("User not found", user_id=str(request.user_id))
            raise EntityNotFoundException("User", str(request.user_id))

        # Check if user is already a member
        existing_member = await self._session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_uuid,
                ProjectMemberModel.user_id == request.user_id,
            )
        )
        if existing_member.scalar_one_or_none() is not None:
            logger.warning(
                "User is already a member",
                project_id=project_id,
                user_id=str(request.user_id),
            )
            raise ConflictException(
                f"User {str(request.user_id)} is already a member of this project",
                field="user_id",
            )

        # Create project member
        project_member = ProjectMemberModel(
            project_id=project_uuid,
            user_id=request.user_id,
            role=request.role,
        )
        self._session.add(project_member)
        await self._session.flush()
        await self._session.refresh(project_member)

        # Fetch user details for response
        user_result = await self._session.execute(
            select(UserModel).where(UserModel.id == request.user_id)
        )
        user_model = user_result.scalar_one()

        logger.info(
            "Member added successfully",
            project_id=project_id,
            user_id=str(request.user_id),
            role=request.role,
        )

        return ProjectMemberResponse(
            user_id=project_member.user_id,
            project_id=project_member.project_id,
            role=project_member.role,
            user_name=user_model.name,
            user_email=user_model.email,
            avatar_url=user_model.avatar_url,
            joined_at=project_member.created_at,
        )


class ListProjectMembersUseCase:
    """Use case for listing project members."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            project_repository: Project repository
            session: Database session
        """
        self._project_repository = project_repository
        self._session = session

    async def execute(
        self, project_id: str, page: int = 1, limit: int = 20
    ) -> ProjectMemberListResponse:
        """Execute list project members.

        Args:
            project_id: Project ID
            page: Page number (1-based)
            limit: Number of members per page

        Returns:
            Member list response DTO with pagination

        Raises:
            EntityNotFoundException: If project not found
        """
        from src.infrastructure.database.models import ProjectMemberModel, UserModel

        logger.info(
            "Listing project members",
            project_id=project_id,
            page=page,
            limit=limit,
        )

        # Verify project exists
        project_uuid = UUID(project_id)
        project = await self._project_repository.get_by_id(project_uuid)

        if project is None:
            logger.warning("Project not found", project_id=project_id)
            raise EntityNotFoundException("Project", project_id)

        offset = (page - 1) * limit

        # Count total members
        count_result = await self._session.execute(
            select(func.count())
            .select_from(ProjectMemberModel)
            .where(ProjectMemberModel.project_id == project_uuid)
        )
        total_members: int = count_result.scalar_one()

        # Fetch members with user details
        members_result = await self._session.execute(
            select(ProjectMemberModel, UserModel)
            .join(UserModel, ProjectMemberModel.user_id == UserModel.id)
            .where(ProjectMemberModel.project_id == project_uuid)
            .offset(offset)
            .limit(limit)
            .order_by(ProjectMemberModel.created_at)
        )

        members_list = []
        for project_member, user_model in members_result.all():
            members_list.append(
                ProjectMemberResponse(
                    user_id=project_member.user_id,
                    project_id=project_member.project_id,
                    role=project_member.role,
                    user_name=user_model.name,
                    user_email=user_model.email,
                    avatar_url=user_model.avatar_url,
                    joined_at=project_member.created_at,
                )
            )

        total_pages = ceil(total_members / limit) if total_members > 0 else 0

        return ProjectMemberListResponse(
            members=members_list,
            total=total_members,
            page=page,
            limit=limit,
            pages=total_pages,
        )


class UpdateProjectMemberRoleUseCase:
    """Use case for updating a member's role in a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        user_repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            project_repository: Project repository
            user_repository: User repository
            session: Database session
        """
        self._project_repository = project_repository
        self._user_repository = user_repository
        self._session = session

    async def execute(
        self,
        project_id: str,
        user_id: str,
        request: UpdateProjectMemberRoleRequest,
    ) -> ProjectMemberResponse:
        """Execute update member role.

        Args:
            project_id: Project ID
            user_id: User ID
            request: Update role request

        Returns:
            Updated member response DTO

        Raises:
            EntityNotFoundException: If project, user, or member not found
            ValidationException: If role is invalid
        """
        from src.infrastructure.database.models import ProjectMemberModel, UserModel

        logger.info(
            "Updating project member role",
            project_id=project_id,
            user_id=user_id,
            new_role=request.role,
        )

        # Validate role
        if not Role.is_valid(request.role):
            raise ValidationException(
                f"Invalid role: {request.role}. Must be one of: admin, member, viewer"
            )

        # Verify project exists
        project_uuid = UUID(project_id)
        project = await self._project_repository.get_by_id(project_uuid)

        if project is None:
            logger.warning("Project not found", project_id=project_id)
            raise EntityNotFoundException("Project", project_id)

        # Verify user exists
        user_uuid = UUID(user_id)
        user = await self._user_repository.get_by_id(user_uuid)

        if user is None:
            logger.warning("User not found", user_id=user_id)
            raise EntityNotFoundException("User", user_id)

        # Find existing member
        member_result = await self._session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_uuid,
                ProjectMemberModel.user_id == user_uuid,
            )
        )
        project_member = member_result.scalar_one_or_none()

        if project_member is None:
            logger.warning(
                "Project member not found",
                project_id=project_id,
                user_id=user_id,
            )
            raise EntityNotFoundException(
                "ProjectMember", f"project_id={project_id}, user_id={user_id}"
            )

        # Update role
        project_member.role = request.role
        await self._session.flush()
        await self._session.refresh(project_member)

        # Fetch user details for response
        user_result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_uuid)
        )
        user_model = user_result.scalar_one()

        logger.info(
            "Member role updated successfully",
            project_id=project_id,
            user_id=user_id,
            new_role=request.role,
        )

        return ProjectMemberResponse(
            user_id=project_member.user_id,
            project_id=project_member.project_id,
            role=project_member.role,
            user_name=user_model.name,
            user_email=user_model.email,
            avatar_url=user_model.avatar_url,
            joined_at=project_member.created_at,
        )


class RemoveProjectMemberUseCase:
    """Use case for removing a member from a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            project_repository: Project repository
            session: Database session
        """
        self._project_repository = project_repository
        self._session = session

    async def execute(self, project_id: str, user_id: str) -> None:
        """Execute remove member from project.

        Args:
            project_id: Project ID
            user_id: User ID

        Raises:
            EntityNotFoundException: If project or member not found
        """
        from src.infrastructure.database.models import ProjectMemberModel

        logger.info(
            "Removing member from project",
            project_id=project_id,
            user_id=user_id,
        )

        # Verify project exists
        project_uuid = UUID(project_id)
        project = await self._project_repository.get_by_id(project_uuid)

        if project is None:
            logger.warning("Project not found", project_id=project_id)
            raise EntityNotFoundException("Project", project_id)

        # Find existing member
        user_uuid = UUID(user_id)
        member_result = await self._session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_uuid,
                ProjectMemberModel.user_id == user_uuid,
            )
        )
        project_member = member_result.scalar_one_or_none()

        if project_member is None:
            logger.warning(
                "Project member not found",
                project_id=project_id,
                user_id=user_id,
            )
            raise EntityNotFoundException(
                "ProjectMember", f"project_id={project_id}, user_id={user_id}"
            )

        # Remove member
        await self._session.delete(project_member)
        await self._session.flush()

        logger.info(
            "Member removed successfully",
            project_id=project_id,
            user_id=user_id,
        )

