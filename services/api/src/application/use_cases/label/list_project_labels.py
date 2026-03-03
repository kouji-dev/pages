"""List project labels use case."""

import math
from uuid import UUID

import structlog

from src.application.dtos.label import LabelListResponse, LabelResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import LabelRepository, ProjectRepository

logger = structlog.get_logger()


class ListProjectLabelsUseCase:
    """Use case for listing labels of a project."""

    def __init__(
        self,
        label_repository: LabelRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._label_repository = label_repository
        self._project_repository = project_repository

    async def execute(
        self,
        project_id: str,
        page: int = 1,
        limit: int = 20,
        search: str | None = None,
    ) -> LabelListResponse:
        """List labels for a project with pagination and optional search."""
        logger.info("Listing project labels", project_id=project_id, page=page, limit=limit)
        project_uuid = UUID(project_id)
        project = await self._project_repository.get_by_id(project_uuid)
        if project is None:
            raise EntityNotFoundException("Project", project_id)
        skip = (page - 1) * limit
        labels = await self._label_repository.get_by_project(
            project_uuid, skip=skip, limit=limit, search=search
        )
        total = await self._label_repository.count_by_project(project_uuid, search=search)
        pages = math.ceil(total / limit) if limit > 0 else 0
        return LabelListResponse(
            labels=[
                LabelResponse(
                    id=label.id,
                    project_id=label.project_id,
                    name=label.name,
                    color=label.color,
                    description=label.description,
                    created_at=label.created_at,
                    updated_at=label.updated_at,
                )
                for label in labels
            ],
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )
