"""Update saved filter use case."""

from uuid import UUID

import structlog

from src.application.dtos.saved_filter import (
    SavedFilterResponse,
    UpdateSavedFilterRequest,
)
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories.saved_filter_repository import SavedFilterRepository

logger = structlog.get_logger()


class UpdateSavedFilterUseCase:
    """Use case for updating a saved filter."""

    def __init__(self, saved_filter_repository: SavedFilterRepository) -> None:
        """Initialize use case with dependencies."""
        self._saved_filter_repository = saved_filter_repository

    async def execute(
        self, filter_id: UUID, request: UpdateSavedFilterRequest
    ) -> SavedFilterResponse:
        """Execute update saved filter."""
        logger.info("Updating saved filter", filter_id=str(filter_id))

        saved_filter = await self._saved_filter_repository.get_by_id(filter_id)

        if saved_filter is None:
            logger.warning("Saved filter not found", filter_id=str(filter_id))
            raise EntityNotFoundException("SavedFilter", str(filter_id))

        # Apply updates
        if request.name is not None:
            try:
                saved_filter.update_name(request.name)
            except ValueError as e:
                raise ValidationException(str(e), field="name") from e

        if request.filter_criteria is not None:
            try:
                saved_filter.update_criteria(request.filter_criteria)
            except ValueError as e:
                raise ValidationException(str(e), field="filter_criteria") from e

        # Save to database
        updated_filter = await self._saved_filter_repository.update(saved_filter)

        logger.info("Saved filter updated", filter_id=str(filter_id))

        return SavedFilterResponse.model_validate(
            {
                "id": updated_filter.id,
                "user_id": updated_filter.user_id,
                "project_id": updated_filter.project_id,
                "name": updated_filter.name,
                "filter_criteria": updated_filter.filter_criteria,
                "created_at": updated_filter.created_at,
                "updated_at": updated_filter.updated_at,
            }
        )
