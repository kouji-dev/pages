"""Create saved filter use case."""

from uuid import UUID

import structlog

from src.application.dtos.saved_filter import (
    CreateSavedFilterRequest,
    SavedFilterResponse,
)
from src.domain.entities.saved_filter import SavedFilter
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import ProjectRepository
from src.domain.repositories.saved_filter_repository import SavedFilterRepository

logger = structlog.get_logger()


class CreateSavedFilterUseCase:
    """Use case for creating a saved filter."""

    def __init__(
        self,
        saved_filter_repository: SavedFilterRepository,
        project_repository: ProjectRepository | None = None,
    ) -> None:
        """Initialize use case with dependencies."""
        self._saved_filter_repository = saved_filter_repository
        self._project_repository = project_repository

    async def execute(
        self, user_id: UUID, request: CreateSavedFilterRequest
    ) -> SavedFilterResponse:
        """Execute create saved filter."""
        logger.info("Creating saved filter", user_id=str(user_id), name=request.name)

        # Verify project exists if provided
        if request.project_id:
            if self._project_repository is None:
                raise ValidationException("Project repository not available", field="project_id")
            project = await self._project_repository.get_by_id(request.project_id)
            if project is None:
                logger.warning("Project not found", project_id=str(request.project_id))
                raise EntityNotFoundException("Project", str(request.project_id))

        # Create saved filter entity
        try:
            saved_filter = SavedFilter.create(
                user_id=user_id,
                name=request.name,
                filter_criteria=request.filter_criteria,
                project_id=request.project_id,
            )
        except ValueError as e:
            raise ValidationException(str(e), field="filter") from e

        # Save to database
        created_filter = await self._saved_filter_repository.create(saved_filter)

        logger.info("Saved filter created", filter_id=str(created_filter.id))

        return SavedFilterResponse.model_validate(
            {
                "id": created_filter.id,
                "user_id": created_filter.user_id,
                "project_id": created_filter.project_id,
                "name": created_filter.name,
                "filter_criteria": created_filter.filter_criteria,
                "created_at": created_filter.created_at,
                "updated_at": created_filter.updated_at,
            }
        )
