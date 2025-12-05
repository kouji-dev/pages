"""Permission service interface for role-based access control."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import User
from src.domain.value_objects import Role


class PermissionService(ABC):
    """Interface for permission checking service.

    Defines methods for checking user permissions at organization and project levels.
    """

    @abstractmethod
    async def get_organization_role(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> Role | None:
        """Get user's role in an organization.

        Args:
            user_id: User UUID
            organization_id: Organization UUID

        Returns:
            User's role in the organization, or None if not a member
        """
        pass

    @abstractmethod
    async def get_project_role(
        self,
        user_id: UUID,
        project_id: UUID,
    ) -> Role | None:
        """Get user's role in a project.

        Args:
            user_id: User UUID
            project_id: Project UUID

        Returns:
            User's role in the project, or None if not a member
        """
        pass

    @abstractmethod
    async def can_access_organization(
        self,
        user: User,
        organization_id: UUID,
    ) -> bool:
        """Check if user can access an organization.

        Args:
            user: User entity
            organization_id: Organization UUID

        Returns:
            True if user is a member of the organization
        """
        pass

    @abstractmethod
    async def can_access_project(
        self,
        user: User,
        project_id: UUID,
    ) -> bool:
        """Check if user can access a project.

        Args:
            user: User entity
            project_id: Project UUID

        Returns:
            True if user can access the project (via organization or project membership)
        """
        pass

    @abstractmethod
    async def can_manage_organization(
        self,
        user: User,
        organization_id: UUID,
    ) -> bool:
        """Check if user can manage an organization.

        Args:
            user: User entity
            organization_id: Organization UUID

        Returns:
            True if user is admin of the organization
        """
        pass

    @abstractmethod
    async def can_edit_content(
        self,
        user: User,
        organization_id: UUID,
        project_id: UUID | None = None,
    ) -> bool:
        """Check if user can edit content.

        Args:
            user: User entity
            organization_id: Organization UUID
            project_id: Optional project UUID for project-specific checks

        Returns:
            True if user has admin or member role
        """
        pass
