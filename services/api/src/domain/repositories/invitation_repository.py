"""Invitation repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Invitation
from src.domain.value_objects import Email


class InvitationRepository(ABC):
    """Abstract invitation repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, invitation: Invitation) -> Invitation:
        """Create a new invitation.

        Args:
            invitation: Invitation entity to create

        Returns:
            Created invitation with persisted data

        Raises:
            ConflictException: If invitation with same token already exists
        """
        ...

    @abstractmethod
    async def get_by_id(self, invitation_id: UUID) -> Invitation | None:
        """Get invitation by ID.

        Args:
            invitation_id: Invitation UUID

        Returns:
            Invitation if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_token(self, token: str) -> Invitation | None:
        """Get invitation by token.

        Args:
            token: Invitation token

        Returns:
            Invitation if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_pending_by_organization_and_email(
        self, organization_id: UUID, email: Email
    ) -> Invitation | None:
        """Get pending invitation by organization and email.

        Args:
            organization_id: Organization UUID
            email: Invited user email

        Returns:
            Pending invitation if found, None otherwise
        """
        ...

    @abstractmethod
    async def list_by_organization(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 20,
        pending_only: bool = True,
    ) -> list[Invitation]:
        """List invitations for an organization.

        Args:
            organization_id: Organization UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            pending_only: If True, only return pending (not accepted) invitations

        Returns:
            List of invitations
        """
        ...

    @abstractmethod
    async def update(self, invitation: Invitation) -> Invitation:
        """Update an existing invitation.

        Args:
            invitation: Invitation entity with updated data

        Returns:
            Updated invitation

        Raises:
            EntityNotFoundException: If invitation not found
        """
        ...

    @abstractmethod
    async def delete(self, invitation_id: UUID) -> None:
        """Delete an invitation.

        Args:
            invitation_id: Invitation UUID

        Raises:
            EntityNotFoundException: If invitation not found
        """
        ...

    @abstractmethod
    async def exists_by_token(self, token: str) -> bool:
        """Check if invitation with token exists.

        Args:
            token: Token to check

        Returns:
            True if invitation exists, False otherwise
        """
        ...
