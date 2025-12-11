"""Get space use case."""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.page import PageListItemResponse
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
            session: Database session for counting pages and fetching recent pages
        """
        self._space_repository = space_repository
        self._session = session

    async def execute(self, space_id: str) -> SpaceResponse:
        """Execute get space.

        Args:
            space_id: Space ID

        Returns:
            Space response DTO with page count and recent pages

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
        count_result = await self._session.execute(
            select(func.count()).select_from(PageModel).where(PageModel.space_id == space_uuid)
        )
        page_count: int = count_result.scalar_one()

        # Get recent pages (up to 5, ordered by updated_at DESC)
        recent_pages_result = await self._session.execute(
            select(PageModel)
            .where(PageModel.space_id == space_uuid)
            .order_by(PageModel.updated_at.desc())
            .limit(5)
        )
        recent_pages_models = recent_pages_result.scalars().all()

        recent_pages = [
            PageListItemResponse(
                id=page.id,
                space_id=page.space_id,
                title=page.title,
                slug=page.slug,
                parent_id=page.parent_id,
                created_by=page.created_by,
                updated_by=page.updated_by,
                position=page.position,
                created_at=page.created_at,
                updated_at=page.updated_at,
            )
            for page in recent_pages_models
        ]

        return SpaceResponse(
            id=space.id,
            organization_id=space.organization_id,
            name=space.name,
            key=space.key,
            description=space.description,
            settings=space.settings,
            page_count=page_count,
            recent_pages=recent_pages,
            created_at=space.created_at,
            updated_at=space.updated_at,
        )
