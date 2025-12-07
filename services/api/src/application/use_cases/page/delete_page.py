"""Delete page use case."""

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageRepository

logger = structlog.get_logger()


class DeletePageUseCase:
    """Use case for deleting a page."""

    def __init__(self, page_repository: PageRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            page_repository: Page repository
        """
        self._page_repository = page_repository

    async def execute(self, page_id: str) -> None:
        """Execute delete page (soft delete).

        Args:
            page_id: Page ID

        Raises:
            EntityNotFoundException: If page not found
        """
        from uuid import UUID

        logger.info("Deleting page", page_id=page_id)

        page_uuid = UUID(page_id)
        page = await self._page_repository.get_by_id(page_uuid)

        if page is None:
            logger.warning("Page not found for deletion", page_id=page_id)
            raise EntityNotFoundException("Page", page_id)

        # Soft delete
        page.delete()
        await self._page_repository.update(page)

        logger.info("Page deleted", page_id=page_id)
