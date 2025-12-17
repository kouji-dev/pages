"""Get saved filter use case."""

from uuid import UUID

import structlog

from src.application.dtos.saved_filter import SavedFilterResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.saved_filter_repository import SavedFilterRepository

logger = structlog.get_logger()


class GetSavedFilterUseCase:
    """Use case for getting a saved filter."""

    def __init__(self, saved_filter_repository: SavedFilterRepository) -> None:
        """Initialize use case with dependencies."""
        self._saved_filter_repository = saved_filter_repository

    async def execute(self, filter_id: UUID) -> SavedFilterResponse:
        """Execute get saved filter."""
        logger.info("Getting saved filter", filter_id=str(filter_id))

        saved_filter = await self._saved_filter_repository.get_by_id(filter_id)

        if saved_filter is None:
            logger.warning("Saved filter not found", filter_id=str(filter_id))
            raise EntityNotFoundException("SavedFilter", str(filter_id))

        return SavedFilterResponse.model_validate(
            {
                "id": saved_filter.id,
                "user_id": saved_filter.user_id,
                "project_id": saved_filter.project_id,
                "name": saved_filter.name,
                "filter_criteria": saved_filter.filter_criteria,
                "created_at": saved_filter.created_at,
                "updated_at": saved_filter.updated_at,
            }
        )
