"""Delete saved filter use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.saved_filter_repository import SavedFilterRepository

logger = structlog.get_logger()


class DeleteSavedFilterUseCase:
    """Use case for deleting a saved filter."""

    def __init__(self, saved_filter_repository: SavedFilterRepository) -> None:
        """Initialize use case with dependencies."""
        self._saved_filter_repository = saved_filter_repository

    async def execute(self, filter_id: UUID) -> None:
        """Execute delete saved filter."""
        logger.info("Deleting saved filter", filter_id=str(filter_id))

        saved_filter = await self._saved_filter_repository.get_by_id(filter_id)
        if saved_filter is None:
            logger.warning("Saved filter not found", filter_id=str(filter_id))
            raise EntityNotFoundException("SavedFilter", str(filter_id))

        await self._saved_filter_repository.delete(filter_id)

        logger.info("Saved filter deleted", filter_id=str(filter_id))
