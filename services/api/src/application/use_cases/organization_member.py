"""Organization member management use cases."""

from math import ceil
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.organization_member import (
    AddMemberRequest,
    OrganizationMemberListResponse,
    OrganizationMemberResponse,
    UpdateMemberRoleRequest,
)
from src.domain.exceptions import ConflictException, EntityNotFoundException, ValidationException
from src.domain.repositories import OrganizationRepository, UserRepository
from src.domain.value_objects import Role

logger = structlog.get_logger()


class AddOrganizationMemberUseCase:
    """Use case for adding a member to an organization."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        user_repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            organization_repository: Organization repository
            user_repository: User repository
            session: Database session
        """
        self._organization_repository = organization_repository
        self._user_repository = user_repository
        self._session = session

    async def execute(
        self, organization_id: str, request: AddMemberRequest
    ) -> OrganizationMemberResponse:
        """Execute add member to organization.

        Args:
            organization_id: Organization ID
            request: Add member request

        Returns:
            Added member response DTO

        Raises:
            EntityNotFoundException: If organization or user not found
            ConflictException: If user is already a member
            ValidationException: If role is invalid
        """
        from src.infrastructure.database.models import OrganizationMemberModel, UserModel

        logger.info(
            "Adding member to organization",
            organization_id=organization_id,
            user_id=str(request.user_id),
            role=request.role,
        )

        # Validate role
        if not Role.is_valid(request.role):
            raise ValidationException(
                f"Invalid role: {request.role}. Must be one of: admin, member, viewer"
            )

        # Verify organization exists
        org_uuid = UUID(organization_id)
        organization = await self._organization_repository.get_by_id(org_uuid)

        if organization is None:
            logger.warning("Organization not found", organization_id=organization_id)
            raise EntityNotFoundException("Organization", organization_id)

        # Verify user exists
        user = await self._user_repository.get_by_id(request.user_id)

        if user is None:
            logger.warning("User not found", user_id=str(request.user_id))
            raise EntityNotFoundException("User", str(request.user_id))

        # Check if user is already a member
        existing_member = await self._session.execute(
            select(OrganizationMemberModel).where(
                OrganizationMemberModel.organization_id == org_uuid,
                OrganizationMemberModel.user_id == request.user_id,
            )
        )
        if existing_member.scalar_one_or_none() is not None:
            logger.warning(
                "User is already a member",
                organization_id=organization_id,
                user_id=str(request.user_id),
            )
            raise ConflictException(
                f"User {str(request.user_id)} is already a member of this organization",
                field="user_id",
            )

        # Create organization member
        org_member = OrganizationMemberModel(
            organization_id=org_uuid,
            user_id=request.user_id,
            role=request.role,
        )
        self._session.add(org_member)
        await self._session.flush()
        await self._session.refresh(org_member)

        # Fetch user details for response
        user_result = await self._session.execute(
            select(UserModel).where(UserModel.id == request.user_id)
        )
        user_model = user_result.scalar_one()

        logger.info(
            "Member added successfully",
            organization_id=organization_id,
            user_id=str(request.user_id),
            role=request.role,
        )

        return OrganizationMemberResponse(
            user_id=org_member.user_id,
            organization_id=org_member.organization_id,
            role=org_member.role,
            user_name=user_model.name,
            user_email=user_model.email,
            avatar_url=user_model.avatar_url,
            joined_at=org_member.created_at,
        )


class ListOrganizationMembersUseCase:
    """Use case for listing organization members."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            organization_repository: Organization repository
            session: Database session
        """
        self._organization_repository = organization_repository
        self._session = session

    async def execute(
        self, organization_id: str, page: int = 1, limit: int = 20
    ) -> OrganizationMemberListResponse:
        """Execute list organization members.

        Args:
            organization_id: Organization ID
            page: Page number (1-based)
            limit: Number of members per page

        Returns:
            Member list response DTO with pagination

        Raises:
            EntityNotFoundException: If organization not found
        """
        from src.infrastructure.database.models import OrganizationMemberModel, UserModel

        logger.info(
            "Listing organization members",
            organization_id=organization_id,
            page=page,
            limit=limit,
        )

        # Verify organization exists
        org_uuid = UUID(organization_id)
        organization = await self._organization_repository.get_by_id(org_uuid)

        if organization is None:
            logger.warning("Organization not found", organization_id=organization_id)
            raise EntityNotFoundException("Organization", organization_id)

        offset = (page - 1) * limit

        # Count total members
        count_result = await self._session.execute(
            select(func.count())
            .select_from(OrganizationMemberModel)
            .where(OrganizationMemberModel.organization_id == org_uuid)
        )
        total_members: int = count_result.scalar_one()

        # Fetch members with user details
        members_result = await self._session.execute(
            select(OrganizationMemberModel, UserModel)
            .join(UserModel, OrganizationMemberModel.user_id == UserModel.id)
            .where(OrganizationMemberModel.organization_id == org_uuid)
            .offset(offset)
            .limit(limit)
            .order_by(OrganizationMemberModel.created_at)
        )

        members_list = []
        for org_member, user_model in members_result.all():
            members_list.append(
                OrganizationMemberResponse(
                    user_id=org_member.user_id,
                    organization_id=org_member.organization_id,
                    role=org_member.role,
                    user_name=user_model.name,
                    user_email=user_model.email,
                    avatar_url=user_model.avatar_url,
                    joined_at=org_member.created_at,
                )
            )

        total_pages = ceil(total_members / limit) if total_members > 0 else 0

        return OrganizationMemberListResponse(
            members=members_list,
            total=total_members,
            page=page,
            limit=limit,
            pages=total_pages,
        )


class UpdateOrganizationMemberRoleUseCase:
    """Use case for updating a member's role in an organization."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        user_repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            organization_repository: Organization repository
            user_repository: User repository
            session: Database session
        """
        self._organization_repository = organization_repository
        self._user_repository = user_repository
        self._session = session

    async def execute(
        self,
        organization_id: str,
        user_id: str,
        request: UpdateMemberRoleRequest,
        admin_user_id: str,
    ) -> OrganizationMemberResponse:
        """Execute update member role.

        Args:
            organization_id: Organization ID
            user_id: User ID of the member to update
            request: Update role request
            admin_user_id: ID of the admin performing the update

        Returns:
            Updated member response DTO

        Raises:
            EntityNotFoundException: If organization, user, or member not found
            ValidationException: If role is invalid or would remove last admin
        """
        from src.infrastructure.database.models import OrganizationMemberModel, UserModel

        logger.info(
            "Updating member role",
            organization_id=organization_id,
            user_id=user_id,
            new_role=request.role,
            admin_user_id=admin_user_id,
        )

        # Validate role
        if not Role.is_valid(request.role):
            raise ValidationException(
                f"Invalid role: {request.role}. Must be one of: admin, member, viewer"
            )

        # Verify organization exists
        org_uuid = UUID(organization_id)
        organization = await self._organization_repository.get_by_id(org_uuid)

        if organization is None:
            logger.warning("Organization not found", organization_id=organization_id)
            raise EntityNotFoundException("Organization", organization_id)

        # Verify target user exists
        target_user_uuid = UUID(user_id)
        target_user = await self._user_repository.get_by_id(target_user_uuid)

        if target_user is None:
            logger.warning("User not found", user_id=user_id)
            raise EntityNotFoundException("User", user_id)

        # Get current member record
        member_result = await self._session.execute(
            select(OrganizationMemberModel).where(
                OrganizationMemberModel.organization_id == org_uuid,
                OrganizationMemberModel.user_id == target_user_uuid,
            )
        )
        org_member = member_result.scalar_one_or_none()

        if org_member is None:
            logger.warning(
                "Member not found",
                organization_id=organization_id,
                user_id=user_id,
            )
            raise EntityNotFoundException("Organization member", f"{organization_id}/{user_id}")

        old_role = org_member.role

        # Prevent removing last admin (only if changing from admin to non-admin)
        if old_role == Role.ADMIN.value and request.role != Role.ADMIN.value:
            admin_count_result = await self._session.execute(
                select(func.count())
                .select_from(OrganizationMemberModel)
                .where(
                    OrganizationMemberModel.organization_id == org_uuid,
                    OrganizationMemberModel.role == Role.ADMIN.value,
                )
            )
            admin_count: int = admin_count_result.scalar_one()

            if admin_count <= 1:
                logger.warning(
                    "Cannot remove last admin",
                    organization_id=organization_id,
                    user_id=user_id,
                )
                raise ValidationException(
                    "Cannot remove the last admin from the organization. "
                    "Please assign another admin first."
                )

        # Update role
        org_member.role = request.role
        await self._session.flush()
        await self._session.refresh(org_member)

        # Fetch user details for response
        user_result = await self._session.execute(
            select(UserModel).where(UserModel.id == target_user_uuid)
        )
        user_model = user_result.scalar_one()

        logger.info(
            "Member role updated successfully",
            organization_id=organization_id,
            user_id=user_id,
            old_role=old_role,
            new_role=request.role,
        )

        return OrganizationMemberResponse(
            user_id=org_member.user_id,
            organization_id=org_member.organization_id,
            role=org_member.role,
            user_name=user_model.name,
            user_email=user_model.email,
            avatar_url=user_model.avatar_url,
            joined_at=org_member.created_at,
        )


class RemoveOrganizationMemberUseCase:
    """Use case for removing a member from an organization."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            organization_repository: Organization repository
            session: Database session
        """
        self._organization_repository = organization_repository
        self._session = session

    async def execute(self, organization_id: str, user_id: str, requester_user_id: str) -> None:
        """Execute remove member from organization.

        Args:
            organization_id: Organization ID
            user_id: User ID of the member to remove
            requester_user_id: ID of the user requesting the removal

        Raises:
            EntityNotFoundException: If organization or member not found
            ValidationException: If trying to remove last admin
        """
        from src.infrastructure.database.models import OrganizationMemberModel

        logger.info(
            "Removing member from organization",
            organization_id=organization_id,
            user_id=user_id,
            requester_user_id=requester_user_id,
        )

        # Verify organization exists
        org_uuid = UUID(organization_id)
        organization = await self._organization_repository.get_by_id(org_uuid)

        if organization is None:
            logger.warning("Organization not found", organization_id=organization_id)
            raise EntityNotFoundException("Organization", organization_id)

        # Get member record
        target_user_uuid = UUID(user_id)
        member_result = await self._session.execute(
            select(OrganizationMemberModel).where(
                OrganizationMemberModel.organization_id == org_uuid,
                OrganizationMemberModel.user_id == target_user_uuid,
            )
        )
        org_member = member_result.scalar_one_or_none()

        if org_member is None:
            logger.warning(
                "Member not found",
                organization_id=organization_id,
                user_id=user_id,
            )
            raise EntityNotFoundException("Organization member", f"{organization_id}/{user_id}")

        # Prevent removing last admin
        if org_member.role == Role.ADMIN.value:
            admin_count_result = await self._session.execute(
                select(func.count())
                .select_from(OrganizationMemberModel)
                .where(
                    OrganizationMemberModel.organization_id == org_uuid,
                    OrganizationMemberModel.role == Role.ADMIN.value,
                )
            )
            admin_count: int = admin_count_result.scalar_one()

            if admin_count <= 1:
                logger.warning(
                    "Cannot remove last admin",
                    organization_id=organization_id,
                    user_id=user_id,
                )
                raise ValidationException(
                    "Cannot remove the last admin from the organization. "
                    "Please assign another admin first."
                )

        # Remove member
        await self._session.delete(org_member)
        await self._session.flush()

        logger.info(
            "Member removed successfully",
            organization_id=organization_id,
            user_id=user_id,
        )
