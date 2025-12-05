"""Permission service implementation."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import User
from src.domain.services import PermissionService
from src.domain.value_objects import Role


class DatabasePermissionService(PermissionService):
    """Permission service implementation using database queries."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize permission service with database session.

        Args:
            session: Async database session
        """
        self._session = session

    async def get_organization_role(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> Role | None:
        """Get user's role in an organization."""
        from src.infrastructure.database.models import OrganizationMemberModel

        result = await self._session.execute(
            select(OrganizationMemberModel.role).where(
                OrganizationMemberModel.organization_id == organization_id,
                OrganizationMemberModel.user_id == user_id,
            )
        )
        role_str = result.scalar_one_or_none()

        if role_str and Role.is_valid(role_str):
            return Role(role_str)
        return None

    async def get_project_role(
        self,
        user_id: UUID,
        project_id: UUID,
    ) -> Role | None:
        """Get user's role in a project."""
        from src.infrastructure.database.models import ProjectMemberModel

        result = await self._session.execute(
            select(ProjectMemberModel.role).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
            )
        )
        role_str = result.scalar_one_or_none()

        if role_str and Role.is_valid(role_str):
            return Role(role_str)
        return None

    async def can_access_organization(
        self,
        user: User,
        organization_id: UUID,
    ) -> bool:
        """Check if user can access an organization."""
        role = await self.get_organization_role(user.id, organization_id)
        return role is not None

    async def can_access_project(
        self,
        user: User,
        project_id: UUID,
    ) -> bool:
        """Check if user can access a project."""
        from src.infrastructure.database.models import (
            OrganizationMemberModel,
            ProjectMemberModel,
            ProjectModel,
        )

        # Check direct project membership
        project_member = await self._session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user.id,
            )
        )
        if project_member.scalar_one_or_none():
            return True

        # Check organization membership (org members can access projects)
        project = await self._session.execute(
            select(ProjectModel.organization_id).where(ProjectModel.id == project_id)
        )
        org_id = project.scalar_one_or_none()

        if org_id:
            org_member = await self._session.execute(
                select(OrganizationMemberModel).where(
                    OrganizationMemberModel.organization_id == org_id,
                    OrganizationMemberModel.user_id == user.id,
                )
            )
            return org_member.scalar_one_or_none() is not None

        return False

    async def can_manage_organization(
        self,
        user: User,
        organization_id: UUID,
    ) -> bool:
        """Check if user can manage an organization."""
        role = await self.get_organization_role(user.id, organization_id)
        return role == Role.ADMIN

    async def can_edit_content(
        self,
        user: User,
        organization_id: UUID,
        project_id: UUID | None = None,
    ) -> bool:
        """Check if user can edit content."""
        # Check organization role first
        org_role = await self.get_organization_role(user.id, organization_id)
        if org_role and org_role.can_edit_content():
            return True

        # If checking project-specific, check project role
        if project_id:
            project_role = await self.get_project_role(user.id, project_id)
            if project_role and project_role.can_edit_content():
                return True

        return False
