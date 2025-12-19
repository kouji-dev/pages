"""List page versions use case."""

from math import ceil
from uuid import UUID

import structlog

from src.application.dtos.page_version import (
    PageVersionListItemResponse,
    PageVersionListResponse,
)
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageRepository, PageVersionRepository

logger = structlog.get_logger()


class ListPageVersionsUseCase:
    """Use case for listing page versions with pagination."""

    def __init__(
        self,
        page_repository: PageRepository,
        page_version_repository: PageVersionRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            page_repository: Page repository
            page_version_repository: Page version repository
        """
        self._page_repository = page_repository
        self._page_version_repository = page_version_repository

    async def execute(
        self,
        page_id: str,
        page: int = 1,
        limit: int = 20,
    ) -> PageVersionListResponse:
        """Execute list page versions.

        Args:
            page_id: Page ID
            page: Page number (1-based)
            limit: Number of versions per page

        Returns:
            Page version list response DTO with pagination metadata

        Raises:
            EntityNotFoundException: If page not found
        """
        logger.info("Listing page versions", page_id=page_id, page=page, limit=limit)

        page_uuid = UUID(page_id)
        # Verify page exists
        page_entity = await self._page_repository.get_by_id(page_uuid)

        if page_entity is None:
            logger.warning("Page not found for listing versions", page_id=page_id)
            raise EntityNotFoundException("Page", page_id)

        offset = (page - 1) * limit

        versions = await self._page_version_repository.get_all(
            page_id=page_uuid,
            skip=offset,
            limit=limit,
        )
        total = await self._page_version_repository.count(page_uuid)

        # Calculate total pages
        pages_count = ceil(total / limit) if total > 0 else 0

        version_responses = [
            PageVersionListItemResponse(
                id=version.id,
                page_id=version.page_id,
                version_number=version.version_number,
                title=version.title,
                created_by=version.created_by,
                created_at=version.created_at,
            )
            for version in versions
        ]

        logger.info("Page versions listed", page_id=page_id, total=total)

        return PageVersionListResponse(
            versions=version_responses,
            total=total,
            page=page,
            limit=limit,
            pages_count=pages_count,
        )
