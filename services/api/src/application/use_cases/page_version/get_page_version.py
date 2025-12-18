"""Get page version use case."""

from uuid import UUID

import structlog

from src.application.dtos.page_version import PageVersionResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageVersionRepository

logger = structlog.get_logger()


class GetPageVersionUseCase:
    """Use case for getting a page version by ID."""

    def __init__(self, page_version_repository: PageVersionRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            page_version_repository: Page version repository
        """
        self._page_version_repository = page_version_repository

    async def execute(self, version_id: str) -> PageVersionResponse:
        """Execute get page version.

        Args:
            version_id: Page version ID

        Returns:
            Page version response DTO

        Raises:
            EntityNotFoundException: If version not found
        """
        logger.info("Getting page version", version_id=version_id)

        version_uuid = UUID(version_id)
        version = await self._page_version_repository.get_by_id(version_uuid)

        if version is None:
            logger.warning("Page version not found", version_id=version_id)
            raise EntityNotFoundException("PageVersion", version_id)

        logger.info("Page version retrieved", version_id=version_id)

        return PageVersionResponse(
            id=version.id,
            page_id=version.page_id,
            version_number=version.version_number,
            title=version.title,
            content=version.content,
            created_by=version.created_by,
            created_at=version.created_at,
        )
