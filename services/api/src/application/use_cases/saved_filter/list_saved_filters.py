"""List saved filters use case."""

from uuid import UUID

import structlog

from src.application.dtos.saved_filter import SavedFilterListResponse, SavedFilterResponse
from src.domain.repositories.saved_filter_repository import SavedFilterRepository

logger = structlog.get_logger()


class ListSavedFiltersUseCase:
    """Use case for listing saved filters."""

    def __init__(self, saved_filter_repository: SavedFilterRepository) -> None:
        """Initialize use case with dependencies."""
        self._saved_filter_repository = saved_filter_repository

    async def execute(
        self, user_id: UUID, project_id: UUID | None = None
    ) -> SavedFilterListResponse:
        """Execute list saved filters."""
        logger.info("Listing saved filters", user_id=str(user_id), project_id=str(project_id))

        if project_id:
            filters = await self._saved_filter_repository.get_by_user_and_project(
                user_id, project_id
            )
        else:
            filters = await self._saved_filter_repository.get_by_user_id(user_id)

        filter_items = [
            SavedFilterResponse.model_validate(
                {
                    "id": f.id,
                    "user_id": f.user_id,
                    "project_id": f.project_id,
                    "name": f.name,
                    "filter_criteria": f.filter_criteria,
                    "created_at": f.created_at,
                    "updated_at": f.updated_at,
                }
            )
            for f in filters
        ]

        return SavedFilterListResponse(filters=filter_items, total=len(filter_items))
