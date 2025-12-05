"""Organization management use cases."""

import structlog
from math import ceil
from uuid import UUID

from src.application.dtos.organization import (
    CreateOrganizationRequest,
    OrganizationListResponse,
    OrganizationListItemResponse,
    OrganizationResponse,
    UpdateOrganizationRequest,
)
from src.domain.entities import Organization
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import OrganizationRepository, UserRepository

logger = structlog.get_logger()


class CreateOrganizationUseCase:
    """Use case for creating an organization."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        user_repository: UserRepository,
        session,  # AsyncSession from SQLAlchemy
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            organization_repository: Organization repository
            user_repository: User repository to verify creator exists
            session: Database session for creating organization member
        """
        self._organization_repository = organization_repository
        self._user_repository = user_repository
        self._session = session

    async def execute(
        self, request: CreateOrganizationRequest, creator_user_id: str
    ) -> OrganizationResponse:
        """Execute organization creation.

        Args:
            request: Organization creation request
            creator_user_id: ID of the user creating the organization

        Returns:
            Created organization response DTO with member count

        Raises:
            EntityNotFoundException: If creator user not found
            ConflictException: If slug already exists
        """
        from src.infrastructure.database.models import OrganizationMemberModel

        logger.info(
            "Creating organization",
            name=request.name,
            slug=request.slug,
            creator_user_id=creator_user_id,
        )

        # Verify creator exists
        creator_uuid = UUID(creator_user_id)
        creator = await self._user_repository.get_by_id(creator_uuid)

        if creator is None:
            logger.warning("Creator user not found", creator_user_id=creator_user_id)
            raise EntityNotFoundException("User", creator_user_id)

        # Create organization entity
        organization = Organization.create(
            name=request.name,
            slug=request.slug,
            description=request.description,
        )

        # Persist organization
        created_org = await self._organization_repository.create(organization)

        # Create organization member with admin role
        org_member = OrganizationMemberModel(
            organization_id=created_org.id,
            user_id=creator_uuid,
            role="admin",
        )
        self._session.add(org_member)
        await self._session.flush()

        logger.info(
            "Organization created successfully",
            organization_id=str(created_org.id),
            slug=created_org.slug,
        )

        # Return response with member count (1 since we just added the creator)
        return OrganizationResponse(
            id=created_org.id,
            name=created_org.name,
            slug=created_org.slug,
            description=created_org.description,
            settings=created_org.settings,
            member_count=1,
            created_at=created_org.created_at,
            updated_at=created_org.updated_at,
        )


class GetOrganizationUseCase:
    """Use case for retrieving an organization."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        session,  # AsyncSession for counting members
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            organization_repository: Organization repository
            session: Database session for counting members
        """
        self._organization_repository = organization_repository
        self._session = session

    async def execute(self, organization_id: str) -> OrganizationResponse:
        """Execute get organization.

        Args:
            organization_id: Organization ID

        Returns:
            Organization response DTO with member count

        Raises:
            EntityNotFoundException: If organization not found
        """
        from sqlalchemy import func, select
        from src.infrastructure.database.models import OrganizationMemberModel

        logger.info("Getting organization", organization_id=organization_id)

        org_uuid = UUID(organization_id)
        organization = await self._organization_repository.get_by_id(org_uuid)

        if organization is None:
            logger.warning("Organization not found", organization_id=organization_id)
            raise EntityNotFoundException("Organization", organization_id)

        # Count members
        result = await self._session.execute(
            select(func.count())
            .select_from(OrganizationMemberModel)
            .where(OrganizationMemberModel.organization_id == org_uuid)
        )
        member_count: int = result.scalar_one()

        return OrganizationResponse(
            id=organization.id,
            name=organization.name,
            slug=organization.slug,
            description=organization.description,
            settings=organization.settings,
            member_count=member_count,
            created_at=organization.created_at,
            updated_at=organization.updated_at,
        )


class ListOrganizationsUseCase:
    """Use case for listing organizations with pagination."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        session,  # AsyncSession for counting members
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            organization_repository: Organization repository
            session: Database session for counting members
        """
        self._organization_repository = organization_repository
        self._session = session

    async def execute(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20,
        search: str | None = None,
    ) -> OrganizationListResponse:
        """Execute list organizations.

        Args:
            user_id: ID of the user (to filter by membership)
            page: Page number (1-based)
            limit: Number of organizations per page
            search: Optional search query for name or slug

        Returns:
            Organization list response DTO with pagination metadata
        """
        from sqlalchemy import func, select
        from src.infrastructure.database.models import OrganizationMemberModel

        logger.info(
            "Listing organizations",
            user_id=user_id,
            page=page,
            limit=limit,
            search=search,
        )

        user_uuid = UUID(user_id)
        offset = (page - 1) * limit

        if search:
            organizations = await self._organization_repository.search(
                query=search,
                skip=offset,
                limit=limit,
                user_id=user_uuid,
            )
            total_orgs = await self._organization_repository.count(
                user_id=user_uuid,
            )
        else:
            organizations = await self._organization_repository.get_all(
                skip=offset,
                limit=limit,
                user_id=user_uuid,
            )
            total_orgs = await self._organization_repository.count(
                user_id=user_uuid,
            )

        # Get member counts for each organization
        org_list_items = []
        for org in organizations:
            result = await self._session.execute(
                select(func.count())
                .select_from(OrganizationMemberModel)
                .where(OrganizationMemberModel.organization_id == org.id)
            )
            member_count: int = result.scalar_one()

            org_list_items.append(
                OrganizationListItemResponse(
                    id=org.id,
                    name=org.name,
                    slug=org.slug,
                    description=org.description,
                    member_count=member_count,
                    created_at=org.created_at,
                    updated_at=org.updated_at,
                )
            )

        total_pages = ceil(total_orgs / limit) if total_orgs > 0 else 0

        return OrganizationListResponse(
            organizations=org_list_items,
            total=total_orgs,
            page=page,
            limit=limit,
            pages=total_pages,
        )


class UpdateOrganizationUseCase:
    """Use case for updating an organization."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        session,  # AsyncSession for counting members
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            organization_repository: Organization repository
            session: Database session for counting members
        """
        self._organization_repository = organization_repository
        self._session = session

    async def execute(
        self, organization_id: str, request: UpdateOrganizationRequest
    ) -> OrganizationResponse:
        """Execute update organization.

        Args:
            organization_id: Organization ID
            request: Organization update request DTO

        Returns:
            Updated organization response DTO

        Raises:
            EntityNotFoundException: If organization not found
            ConflictException: If slug conflicts with another organization
        """
        from sqlalchemy import func, select
        from src.infrastructure.database.models import OrganizationMemberModel

        logger.info(
            "Updating organization",
            organization_id=organization_id,
            updates=request.model_dump(exclude_unset=True),
        )

        org_uuid = UUID(organization_id)
        organization = await self._organization_repository.get_by_id(org_uuid)

        if organization is None:
            logger.warning("Organization not found", organization_id=organization_id)
            raise EntityNotFoundException("Organization", organization_id)

        # Update fields
        update_data = request.model_dump(exclude_unset=True)

        if "name" in update_data:
            regenerate_slug = "slug" not in update_data
            organization.update_name(update_data["name"], regenerate_slug=regenerate_slug)

        if "slug" in update_data:
            organization.update_slug(update_data["slug"])

        if "description" in update_data:
            organization.update_description(update_data["description"])

        # Persist changes
        updated_org = await self._organization_repository.update(organization)

        # Count members
        result = await self._session.execute(
            select(func.count())
            .select_from(OrganizationMemberModel)
            .where(OrganizationMemberModel.organization_id == org_uuid)
        )
        member_count: int = result.scalar_one()

        logger.info(
            "Organization updated successfully",
            organization_id=organization_id,
            slug=updated_org.slug,
        )

        return OrganizationResponse(
            id=updated_org.id,
            name=updated_org.name,
            slug=updated_org.slug,
            description=updated_org.description,
            settings=updated_org.settings,
            member_count=member_count,
            created_at=updated_org.created_at,
            updated_at=updated_org.updated_at,
        )


class DeleteOrganizationUseCase:
    """Use case for deleting an organization (soft delete)."""

    def __init__(self, organization_repository: OrganizationRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            organization_repository: Organization repository
        """
        self._organization_repository = organization_repository

    async def execute(self, organization_id: str) -> None:
        """Execute delete organization.

        Args:
            organization_id: Organization ID

        Raises:
            EntityNotFoundException: If organization not found
        """
        logger.info("Deleting organization", organization_id=organization_id)

        org_uuid = UUID(organization_id)
        organization = await self._organization_repository.get_by_id(org_uuid)

        if organization is None:
            logger.warning("Organization not found", organization_id=organization_id)
            raise EntityNotFoundException("Organization", organization_id)

        # Soft delete
        organization.delete()
        await self._organization_repository.update(organization)

        logger.info("Organization deleted successfully", organization_id=organization_id)

