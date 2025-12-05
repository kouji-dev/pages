"""SQLAlchemy implementation of InvitationRepository."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Invitation
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import InvitationRepository
from src.domain.value_objects import Email
from src.infrastructure.database.models import InvitationModel


class SQLAlchemyInvitationRepository(InvitationRepository):
    """SQLAlchemy implementation of InvitationRepository.

    Adapts the domain InvitationRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, invitation: Invitation) -> Invitation:
        """Create a new invitation in the database.

        Args:
            invitation: Invitation domain entity

        Returns:
            Created invitation with persisted data

        Raises:
            ConflictException: If invitation with same token already exists
        """
        # Check for existing token
        if await self.exists_by_token(invitation.token):
            raise ConflictException(
                f"Invitation with token '{invitation.token}' already exists", field="token"
            )

        # Create model from entity
        model = InvitationModel(
            id=invitation.id,
            organization_id=invitation.organization_id,
            email=str(invitation.email),
            token=invitation.token,
            role=invitation.role,
            invited_by=invitation.invited_by,
            expires_at=invitation.expires_at,
            accepted_at=invitation.accepted_at,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, invitation_id: UUID) -> Invitation | None:
        """Get invitation by ID.

        Args:
            invitation_id: Invitation UUID

        Returns:
            Invitation if found, None otherwise
        """
        result = await self._session.execute(
            select(InvitationModel).where(InvitationModel.id == invitation_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_token(self, token: str) -> Invitation | None:
        """Get invitation by token.

        Args:
            token: Invitation token

        Returns:
            Invitation if found, None otherwise
        """
        result = await self._session.execute(
            select(InvitationModel).where(InvitationModel.token == token)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

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
        result = await self._session.execute(
            select(InvitationModel).where(
                and_(
                    InvitationModel.organization_id == organization_id,
                    InvitationModel.email == str(email),
                    InvitationModel.accepted_at.is_(None),
                    InvitationModel.expires_at > func.now(),
                )
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

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
        query = select(InvitationModel).where(
            InvitationModel.organization_id == organization_id
        )

        if pending_only:
            query = query.where(
                and_(
                    InvitationModel.accepted_at.is_(None),
                    InvitationModel.expires_at > func.now(),
                )
            )

        query = query.order_by(InvitationModel.created_at.desc()).offset(skip).limit(limit)

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def update(self, invitation: Invitation) -> Invitation:
        """Update an existing invitation.

        Args:
            invitation: Invitation entity with updated data

        Returns:
            Updated invitation

        Raises:
            EntityNotFoundException: If invitation not found
        """
        result = await self._session.execute(
            select(InvitationModel).where(InvitationModel.id == invitation.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Invitation", str(invitation.id))

        # Update model fields
        model.organization_id = invitation.organization_id
        model.email = str(invitation.email)
        model.token = invitation.token
        model.role = invitation.role
        model.invited_by = invitation.invited_by
        model.expires_at = invitation.expires_at
        model.accepted_at = invitation.accepted_at
        model.updated_at = invitation.updated_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, invitation_id: UUID) -> None:
        """Delete an invitation.

        Args:
            invitation_id: Invitation UUID

        Raises:
            EntityNotFoundException: If invitation not found
        """
        result = await self._session.execute(
            select(InvitationModel).where(InvitationModel.id == invitation_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Invitation", str(invitation_id))

        await self._session.delete(model)
        await self._session.flush()

    async def exists_by_token(self, token: str) -> bool:
        """Check if invitation with token exists.

        Args:
            token: Token to check

        Returns:
            True if invitation exists, False otherwise
        """
        result = await self._session.execute(
            select(InvitationModel).where(InvitationModel.token == token)
        )
        return result.scalar_one_or_none() is not None

    def _to_entity(self, model: InvitationModel) -> Invitation:
        """Convert InvitationModel to Invitation domain entity.

        Args:
            model: Database model

        Returns:
            Domain entity
        """
        return Invitation(
            id=model.id,
            organization_id=model.organization_id,
            email=Email(model.email),
            token=model.token,
            role=model.role,
            invited_by=model.invited_by,
            expires_at=model.expires_at,
            accepted_at=model.accepted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

