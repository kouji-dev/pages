"""Update space use case."""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.space import SpaceResponse, UpdateSpaceRequest
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import SpaceRepository
from src.infrastructure.database.models import PageModel

logger = structlog.get_logger()


class UpdateSpaceUseCase:
    """Use case for updating a space."""

    def __init__(
        self,
        space_repository: SpaceRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            space_repository: Space repository
            session: Database session for counting pages
        """
        self._space_repository = space_repository
        self._session = session

    async def execute(self, space_id: str, request: UpdateSpaceRequest) -> SpaceResponse:
        """Execute update space.

        Args:
            space_id: Space ID
            request: Space update request

        Returns:
            Updated space response DTO with page count

        Raises:
            EntityNotFoundException: If space not found
            ConflictException: If space key conflicts with another space
        """
        logger.info("Updating space", space_id=space_id)

        space_uuid = UUID(space_id)
        space = await self._space_repository.get_by_id(space_uuid)

        if space is None:
            logger.warning("Space not found for update", space_id=space_id)
            raise EntityNotFoundException("Space", space_id)

        # Update fields if provided
        if request.name is not None:
            space.update_name(request.name, regenerate_key=False)

        if request.key is not None:
            space.update_key(request.key)

        if request.description is not None:
            space.update_description(request.description)

        # Persist changes
        updated_space = await self._space_repository.update(space)

        # Count pages
        result = await self._session.execute(
            select(func.count()).select_from(PageModel).where(PageModel.space_id == space_uuid)
        )
        page_count: int = result.scalar_one()

        logger.info("Space updated", space_id=space_id)

        return SpaceResponse(
            id=updated_space.id,
            organization_id=updated_space.organization_id,
            name=updated_space.name,
            key=updated_space.key,
            description=updated_space.description,
            settings=updated_space.settings,
            page_count=page_count,
            created_at=updated_space.created_at,
            updated_at=updated_space.updated_at,
        )
