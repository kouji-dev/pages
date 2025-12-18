"""Create page version use case."""

from uuid import UUID

import structlog

from src.application.dtos.page_version import PageVersionResponse
from src.domain.entities import PageVersion
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageRepository, PageVersionRepository

logger = structlog.get_logger()


class CreatePageVersionUseCase:
    """Use case for creating a page version."""

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
        created_by: str | None = None,
    ) -> PageVersionResponse:
        """Execute create page version.

        Creates a new version of the page with current state.

        Args:
            page_id: Page ID
            created_by: ID of the user creating the version

        Returns:
            Created page version response DTO

        Raises:
            EntityNotFoundException: If page not found
        """
        logger.info("Creating page version", page_id=page_id)

        page_uuid = UUID(page_id)
        page = await self._page_repository.get_by_id(page_uuid)

        if page is None:
            logger.warning("Page not found for version creation", page_id=page_id)
            raise EntityNotFoundException("Page", page_id)

        # Get next version number
        version_number = await self._page_version_repository.get_next_version_number(page_uuid)

        # Create version entity
        created_by_uuid = UUID(created_by) if created_by else None
        page_version = PageVersion.create(
            page_id=page_uuid,
            version_number=version_number,
            title=page.title,
            content=page.content,
            created_by=created_by_uuid,
        )

        # Persist version
        created_version = await self._page_version_repository.create(page_version)

        logger.info("Page version created", page_id=page_id, version_number=version_number)

        return PageVersionResponse(
            id=created_version.id,
            page_id=created_version.page_id,
            version_number=created_version.version_number,
            title=created_version.title,
            content=created_version.content,
            created_by=created_version.created_by,
            created_at=created_version.created_at,
        )
