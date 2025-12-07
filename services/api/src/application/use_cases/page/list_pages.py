"""List pages use case."""

from math import ceil
from uuid import UUID

import structlog
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.page import PageListItemResponse, PageListResponse
from src.domain.repositories import PageRepository
from src.infrastructure.database.models import PageModel

logger = structlog.get_logger()


class ListPagesUseCase:
    """Use case for listing pages with pagination."""

    def __init__(
        self,
        page_repository: PageRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            page_repository: Page repository
            session: Database session for counting pages
        """
        self._page_repository = page_repository
        self._session = session

    async def execute(
        self,
        space_id: str,
        page: int = 1,
        limit: int = 20,
        search: str | None = None,
        parent_id: str | None = None,
    ) -> PageListResponse:
        """Execute list pages.

        Args:
            space_id: Space ID
            page: Page number (1-based)
            limit: Number of pages per page
            search: Optional search query for title or content
            parent_id: Optional parent page ID to filter by (None for root pages)

        Returns:
            Page list response DTO with pagination metadata
        """
        space_uuid = UUID(space_id)
        parent_uuid = UUID(parent_id) if parent_id else None
        offset = (page - 1) * limit

        logger.info(
            "Listing pages",
            space_id=space_id,
            page=page,
            limit=limit,
            search=search,
            parent_id=parent_id,
        )

        if search:
            pages = await self._page_repository.search(
                space_id=space_uuid, query=search, skip=offset, limit=limit
            )
            total = await self._count_search_results(space_uuid, search)
        else:
            pages = await self._page_repository.get_all(
                space_id=space_uuid, skip=offset, limit=limit, parent_id=parent_uuid
            )
            total = await self._page_repository.count(space_id=space_uuid, parent_id=parent_uuid)

        # Calculate total pages
        pages_count = ceil(total / limit) if total > 0 else 0

        page_responses = [
            PageListItemResponse(
                id=p.id,
                space_id=p.space_id,
                title=p.title,
                slug=p.slug,
                parent_id=p.parent_id,
                created_by=p.created_by,
                updated_by=p.updated_by,
                position=p.position,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in pages
        ]

        logger.info("Pages listed", count=len(page_responses), total=total, pages=pages_count)

        return PageListResponse(
            pages=page_responses,
            total=total,
            page=page,
            limit=limit,
            pages_count=pages_count,
        )

    async def _count_search_results(self, space_id: UUID, query: str) -> int:
        """Count search results.

        Args:
            space_id: Space UUID
            query: Search query

        Returns:
            Total count of matching pages
        """
        search_pattern = f"%{query}%"

        stmt = (
            select(func.count())
            .select_from(PageModel)
            .where(
                PageModel.space_id == space_id,
                PageModel.deleted_at.is_(None),
                or_(
                    PageModel.title.ilike(search_pattern),
                    PageModel.content.ilike(search_pattern),
                ),
            )
        )

        result = await self._session.execute(stmt)
        count: int = result.scalar_one()
        return count
