"""Create label use case."""

from uuid import UUID

import structlog

from src.application.dtos.label import CreateLabelRequest, LabelResponse
from src.domain.entities import Label
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import LabelRepository, ProjectRepository

logger = structlog.get_logger()


class CreateLabelUseCase:
    """Use case for creating a label."""

    def __init__(
        self,
        label_repository: LabelRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._label_repository = label_repository
        self._project_repository = project_repository

    async def execute(self, project_id: str, request: CreateLabelRequest) -> LabelResponse:
        """Create a new label in a project."""
        logger.info("Creating label", project_id=project_id, name=request.name)
        project_uuid = UUID(project_id)
        project = await self._project_repository.get_by_id(project_uuid)
        if project is None:
            raise EntityNotFoundException("Project", project_id)
        label = Label.create(
            project_id=project_uuid,
            name=request.name,
            color=request.color,
            description=request.description,
        )
        created = await self._label_repository.create(label)
        return LabelResponse(
            id=created.id,
            project_id=created.project_id,
            name=created.name,
            color=created.color,
            description=created.description,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )
