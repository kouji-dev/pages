"""Get space use case."""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.space import SpaceResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import SpaceRepository
from src.infrastructure.database.models import PageModel

logger = structlog.get_logger()


class GetSpaceUseCase:
    """Use case for retrieving a space."""

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

    async def execute(self, space_id: str) -> SpaceResponse:
        """Execute get space.

        Args:
            space_id: Space ID

        Returns:
            Space response DTO with page count

        Raises:
            EntityNotFoundException: If space not found
        """
        logger.info("Getting space", space_id=space_id)

        space_uuid = UUID(space_id)
        space = await self._space_repository.get_by_id(space_uuid)

        if space is None:
            logger.warning("Space not found", space_id=space_id)
            raise EntityNotFoundException("Space", space_id)

        # Count pages
        result = await self._session.execute(
            select(func.count()).select_from(PageModel).where(PageModel.space_id == space_uuid)
        )
        page_count: int = result.scalar_one()

        return SpaceResponse(
            id=space.id,
            organization_id=space.organization_id,
            name=space.name,
            key=space.key,
            description=space.description,
            settings=space.settings,
            page_count=page_count,
            created_at=space.created_at,
            updated_at=space.updated_at,
        )
