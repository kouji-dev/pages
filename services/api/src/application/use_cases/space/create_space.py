"""Create space use case."""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.space import CreateSpaceRequest, SpaceResponse
from src.domain.entities import Space
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import OrganizationRepository, SpaceRepository, UserRepository
from src.infrastructure.database.models import PageModel

logger = structlog.get_logger()


class CreateSpaceUseCase:
    """Use case for creating a space."""

    def __init__(
        self,
        space_repository: SpaceRepository,
        organization_repository: OrganizationRepository,
        user_repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            space_repository: Space repository
            organization_repository: Organization repository to verify organization exists
            user_repository: User repository to verify creator exists
            session: Database session for counting pages
        """
        self._space_repository = space_repository
        self._organization_repository = organization_repository
        self._user_repository = user_repository
        self._session = session

    async def execute(self, request: CreateSpaceRequest, creator_user_id: str) -> SpaceResponse:
        """Execute space creation.

        Args:
            request: Space creation request
            creator_user_id: ID of the user creating the space

        Returns:
            Created space response DTO with page count

        Raises:
            EntityNotFoundException: If organization or creator user not found
            ConflictException: If space key already exists in organization
        """
        logger.info(
            "Creating space",
            name=request.name,
            key=request.key,
            organization_id=str(request.organization_id),
            creator_user_id=creator_user_id,
        )

        # Verify organization exists
        organization = await self._organization_repository.get_by_id(request.organization_id)
        if organization is None:
            logger.warning(
                "Organization not found for space creation",
                organization_id=str(request.organization_id),
            )
            raise EntityNotFoundException("Organization", str(request.organization_id))

        # Verify creator exists
        creator_uuid = UUID(creator_user_id)
        creator = await self._user_repository.get_by_id(creator_uuid)
        if creator is None:
            logger.warning("Creator user not found", creator_user_id=creator_user_id)
            raise EntityNotFoundException("User", creator_user_id)

        # Create space entity
        space = Space.create(
            organization_id=request.organization_id,
            name=request.name,
            key=request.key,
            description=request.description,
        )

        # Persist space
        created_space = await self._space_repository.create(space)

        # Count pages (will be 0 for new space)
        result = await self._session.execute(
            select(func.count())
            .select_from(PageModel)
            .where(PageModel.space_id == created_space.id)
        )
        page_count: int = result.scalar_one()

        logger.info(
            "Space created successfully",
            space_id=str(created_space.id),
            key=created_space.key,
        )

        return SpaceResponse(
            id=created_space.id,
            organization_id=created_space.organization_id,
            name=created_space.name,
            key=created_space.key,
            description=created_space.description,
            settings=created_space.settings,
            page_count=page_count,
            created_at=created_space.created_at,
            updated_at=created_space.updated_at,
        )
