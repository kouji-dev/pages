"""Organization invitation use cases."""

import secrets
import structlog
from math import ceil
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.invitation import (
    AcceptInvitationResponse,
    InvitationListResponse,
    InvitationResponse,
    SendInvitationRequest,
)
from src.domain.entities import Invitation
from src.domain.exceptions import (
    ConflictException,
    EntityNotFoundException,
    ValidationException,
)
from src.domain.repositories import (
    InvitationRepository,
    OrganizationRepository,
    UserRepository,
)
from src.domain.value_objects import Email, Role
from src.infrastructure.database.models import OrganizationMemberModel

logger = structlog.get_logger()


class SendInvitationUseCase:
    """Use case for sending an invitation to join an organization."""

    def __init__(
        self,
        invitation_repository: InvitationRepository,
        organization_repository: OrganizationRepository,
        user_repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            invitation_repository: Invitation repository
            organization_repository: Organization repository
            user_repository: User repository
            session: Database session
        """
        self._invitation_repository = invitation_repository
        self._organization_repository = organization_repository
        self._user_repository = user_repository
        self._session = session

    async def execute(
        self, organization_id: str, request: SendInvitationRequest, invited_by_user_id: str
    ) -> InvitationResponse:
        """Execute send invitation.

        Args:
            organization_id: Organization ID
            request: Send invitation request
            invited_by_user_id: ID of user sending the invitation

        Returns:
            Created invitation response DTO

        Raises:
            EntityNotFoundException: If organization not found
            ConflictException: If user is already a member or invitation already exists
            ValidationException: If role is invalid or email format is invalid
        """
        logger.info(
            "Sending invitation",
            organization_id=organization_id,
            email=request.email,
            role=request.role,
            invited_by=invited_by_user_id,
        )

        # Validate role
        if not Role.is_valid(request.role):
            raise ValidationException(
                f"Invalid role: {request.role}. Must be one of: admin, member, viewer"
            )

        # Create email value object (validates format)
        try:
            email = Email(request.email)
        except Exception as e:
            logger.warning("Invalid email format", email=request.email, error=str(e))
            raise ValidationException(f"Invalid email format: {request.email}", field="email") from e

        # Verify organization exists
        org_uuid = UUID(organization_id)
        organization = await self._organization_repository.get_by_id(org_uuid)

        if organization is None:
            logger.warning("Organization not found", organization_id=organization_id)
            raise EntityNotFoundException("Organization", organization_id)

        # Check if user with this email is already a member
        user = await self._user_repository.get_by_email(email)
        if user is not None:
            existing_member = await self._session.execute(
                select(OrganizationMemberModel).where(
                    OrganizationMemberModel.organization_id == org_uuid,
                    OrganizationMemberModel.user_id == user.id,
                )
            )
            if existing_member.scalar_one_or_none() is not None:
                logger.warning(
                    "User is already a member",
                    organization_id=organization_id,
                    email=request.email,
                )
                raise ConflictException(
                    f"User with email {request.email} is already a member of this organization",
                    field="email",
                )

        # Check if there's already a pending invitation for this email and organization
        existing_invitation = await self._invitation_repository.get_pending_by_organization_and_email(
            org_uuid, email
        )
        if existing_invitation is not None:
            logger.warning(
                "Invitation already exists",
                organization_id=organization_id,
                email=request.email,
            )
            raise ConflictException(
                f"Pending invitation already exists for {request.email}",
                field="email",
            )

        # Generate secure invitation token
        token = secrets.token_urlsafe(32)

        # Create invitation entity
        invited_by_uuid = UUID(invited_by_user_id)
        invitation = Invitation.create(
            organization_id=org_uuid,
            email=email,
            token=token,
            role=request.role,
            invited_by=invited_by_uuid,
            expires_in_days=7,
        )

        # Persist invitation
        created_invitation = await self._invitation_repository.create(invitation)

        # TODO: Send invitation email asynchronously
        # await self._email_service.send_invitation_email(
        #     email=email,
        #     organization_name=organization.name,
        #     invitation_token=token,
        #     invited_by_name=inviter.name,
        # )

        logger.info(
            "Invitation sent successfully",
            invitation_id=str(created_invitation.id),
            organization_id=organization_id,
            email=request.email,
        )

        return InvitationResponse(
            id=created_invitation.id,
            organization_id=created_invitation.organization_id,
            email=str(created_invitation.email),
            role=created_invitation.role,
            invited_by=created_invitation.invited_by,
            expires_at=created_invitation.expires_at,
            accepted_at=created_invitation.accepted_at,
            created_at=created_invitation.created_at,
        )


class AcceptInvitationUseCase:
    """Use case for accepting an invitation to join an organization."""

    def __init__(
        self,
        invitation_repository: InvitationRepository,
        organization_repository: OrganizationRepository,
        user_repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            invitation_repository: Invitation repository
            organization_repository: Organization repository
            user_repository: User repository
            session: Database session
        """
        self._invitation_repository = invitation_repository
        self._organization_repository = organization_repository
        self._user_repository = user_repository
        self._session = session

    async def execute(self, token: str, user_id: str | None = None) -> AcceptInvitationResponse:
        """Execute accept invitation.

        Args:
            token: Invitation token
            user_id: Optional user ID if user is authenticated (must match invitation email)

        Returns:
            Accept invitation response with organization details

        Raises:
            EntityNotFoundException: If invitation not found
            ValidationException: If invitation is expired, already accepted, or email mismatch
            ConflictException: If user is already a member
        """
        logger.info("Accepting invitation", token=token[:10] + "...", user_id=user_id)

        # Get invitation by token
        invitation = await self._invitation_repository.get_by_token(token)

        if invitation is None:
            logger.warning("Invitation not found", token=token[:10] + "...")
            raise EntityNotFoundException("Invitation", token)

        # Validate invitation is not expired
        if invitation.is_expired():
            logger.warning("Invitation expired", invitation_id=str(invitation.id))
            raise ValidationException("Invitation has expired")

        # Validate invitation is not already accepted
        if invitation.is_accepted():
            logger.warning("Invitation already accepted", invitation_id=str(invitation.id))
            raise ValidationException("Invitation has already been accepted")

        # Get organization
        organization = await self._organization_repository.get_by_id(invitation.organization_id)
        if organization is None:
            logger.warning(
                "Organization not found", organization_id=str(invitation.organization_id)
            )
            raise EntityNotFoundException("Organization", str(invitation.organization_id))

        # If user is authenticated, verify email matches
        if user_id is not None:
            user_uuid = UUID(user_id)
            user = await self._user_repository.get_by_id(user_uuid)

            if user is None:
                logger.warning("User not found", user_id=user_id)
                raise EntityNotFoundException("User", user_id)

            if user.email != invitation.email:
                logger.warning(
                    "Email mismatch",
                    invitation_email=str(invitation.email),
                    user_email=str(user.email),
                )
                raise ValidationException(
                    f"Invitation email {str(invitation.email)} does not match user email {str(user.email)}"
                )

            # Check if user is already a member
            existing_member = await self._session.execute(
                select(OrganizationMemberModel).where(
                    OrganizationMemberModel.organization_id == invitation.organization_id,
                    OrganizationMemberModel.user_id == user_uuid,
                )
            )
            if existing_member.scalar_one_or_none() is not None:
                logger.warning(
                    "User is already a member",
                    organization_id=str(invitation.organization_id),
                    user_id=user_id,
                )
                raise ConflictException("User is already a member of this organization")

            # Add user to organization as member
            org_member = OrganizationMemberModel(
                organization_id=invitation.organization_id,
                user_id=user_uuid,
                role=invitation.role,
            )
            self._session.add(org_member)
            await self._session.flush()

            # Mark invitation as accepted
            invitation.accept()
            await self._invitation_repository.update(invitation)

            # TODO: Send welcome notification asynchronously
            # await self._notification_service.send_welcome_notification(
            #     user_id=user_uuid,
            #     organization_id=invitation.organization_id,
            # )

            logger.info(
                "Invitation accepted successfully",
                invitation_id=str(invitation.id),
                organization_id=str(invitation.organization_id),
                user_id=user_id,
            )

            return AcceptInvitationResponse(
                organization_id=organization.id,
                organization_name=organization.name,
                organization_slug=organization.slug,
                role=invitation.role,
                message="Invitation accepted successfully",
            )
        else:
            # User is not authenticated - cannot accept invitation
            logger.warning(
                "Cannot accept invitation: user not authenticated",
                invitation_id=str(invitation.id),
                organization_id=str(invitation.organization_id),
            )
            raise ValidationException("User must be authenticated to accept an invitation")


class ListInvitationsUseCase:
    """Use case for listing invitations for an organization."""

    def __init__(
        self,
        invitation_repository: InvitationRepository,
        organization_repository: OrganizationRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            invitation_repository: Invitation repository
            organization_repository: Organization repository
        """
        self._invitation_repository = invitation_repository
        self._organization_repository = organization_repository

    async def execute(
        self,
        organization_id: str,
        page: int = 1,
        limit: int = 20,
        pending_only: bool = True,
    ) -> InvitationListResponse:
        """Execute list invitations.

        Args:
            organization_id: Organization ID
            page: Page number (1-based)
            limit: Number of items per page
            pending_only: If True, only return pending invitations

        Returns:
            List of invitations response DTO

        Raises:
            EntityNotFoundException: If organization not found
            ValidationException: If page or limit are invalid
        """
        logger.info(
            "Listing invitations",
            organization_id=organization_id,
            page=page,
            limit=limit,
            pending_only=pending_only,
        )

        # Validate pagination parameters
        if page < 1:
            raise ValidationException("Page must be >= 1", field="page")
        if limit < 1 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100", field="limit")

        # Verify organization exists
        org_uuid = UUID(organization_id)
        organization = await self._organization_repository.get_by_id(org_uuid)

        if organization is None:
            logger.warning("Organization not found", organization_id=organization_id)
            raise EntityNotFoundException("Organization", organization_id)

        # Calculate skip
        skip = (page - 1) * limit

        # Get invitations
        invitations = await self._invitation_repository.list_by_organization(
            org_uuid, skip=skip, limit=limit, pending_only=pending_only
        )

        # Convert to response DTOs
        invitation_responses = [
            InvitationResponse(
                id=inv.id,
                organization_id=inv.organization_id,
                email=str(inv.email),
                role=inv.role,
                invited_by=inv.invited_by,
                expires_at=inv.expires_at,
                accepted_at=inv.accepted_at,
                created_at=inv.created_at,
            )
            for inv in invitations
        ]

        # TODO: Get total count for pagination (would need count method in repository)
        # For now, estimate based on returned items
        total = len(invitation_responses) if page == 1 else page * limit
        pages = ceil(total / limit) if total > 0 else 1

        return InvitationListResponse(
            invitations=invitation_responses,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )


class CancelInvitationUseCase:
    """Use case for canceling an invitation."""

    def __init__(
        self,
        invitation_repository: InvitationRepository,
        organization_repository: OrganizationRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            invitation_repository: Invitation repository
            organization_repository: Organization repository
        """
        self._invitation_repository = invitation_repository
        self._organization_repository = organization_repository

    async def execute(self, invitation_id: str) -> None:
        """Execute cancel invitation.

        Args:
            invitation_id: Invitation ID

        Raises:
            EntityNotFoundException: If invitation not found
            ValidationException: If invitation is already accepted
        """
        logger.info("Canceling invitation", invitation_id=invitation_id)

        invitation_uuid = UUID(invitation_id)
        invitation = await self._invitation_repository.get_by_id(invitation_uuid)

        if invitation is None:
            logger.warning("Invitation not found", invitation_id=invitation_id)
            raise EntityNotFoundException("Invitation", invitation_id)

        # Validate invitation is not already accepted
        if invitation.is_accepted():
            logger.warning("Cannot cancel accepted invitation", invitation_id=invitation_id)
            raise ValidationException("Cannot cancel an invitation that has already been accepted")

        # Delete invitation
        await self._invitation_repository.delete(invitation_uuid)

        logger.info("Invitation canceled successfully", invitation_id=invitation_id)

