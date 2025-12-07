"""Get page use case."""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.page import PageResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageRepository
from src.infrastructure.database.models import CommentModel

logger = structlog.get_logger()


class GetPageUseCase:
    """Use case for retrieving a page."""

    def __init__(
        self,
        page_repository: PageRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            page_repository: Page repository
            session: Database session for counting comments
        """
        self._page_repository = page_repository
        self._session = session

    async def execute(self, page_id: str) -> PageResponse:
        """Execute get page.

        Args:
            page_id: Page ID

        Returns:
            Page response DTO with comment count

        Raises:
            EntityNotFoundException: If page not found
        """
        logger.info("Getting page", page_id=page_id)

        page_uuid = UUID(page_id)
        page = await self._page_repository.get_by_id(page_uuid)

        if page is None:
            logger.warning("Page not found", page_id=page_id)
            raise EntityNotFoundException("Page", page_id)

        # Count comments
        result = await self._session.execute(
            select(func.count()).select_from(CommentModel).where(CommentModel.page_id == page_uuid)
        )
        comment_count: int = result.scalar_one()

        return PageResponse(
            id=page.id,
            space_id=page.space_id,
            title=page.title,
            slug=page.slug,
            content=page.content,
            parent_id=page.parent_id,
            created_by=page.created_by,
            updated_by=page.updated_by,
            position=page.position,
            comment_count=comment_count,
            created_at=page.created_at,
            updated_at=page.updated_at,
        )
