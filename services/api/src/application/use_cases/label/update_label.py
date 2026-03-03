"""Update label use case."""

from uuid import UUID

import structlog

from src.application.dtos.label import LabelResponse, UpdateLabelRequest
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import LabelRepository

logger = structlog.get_logger()


class UpdateLabelUseCase:
    """Use case for updating a label."""

    def __init__(self, label_repository: LabelRepository) -> None:
        self._label_repository = label_repository

    async def execute(self, label_id: str, request: UpdateLabelRequest) -> LabelResponse:
        """Update an existing label."""
        logger.info("Updating label", label_id=label_id)
        label_uuid = UUID(label_id)
        label = await self._label_repository.get_by_id(label_uuid)
        if label is None:
            raise EntityNotFoundException("Label", label_id)
        if request.name is not None:
            label.update_name(request.name)
        if request.color is not None:
            label.update_color(request.color)
        if request.description is not None:
            label.update_description(request.description)
        updated = await self._label_repository.update(label)
        return LabelResponse(
            id=updated.id,
            project_id=updated.project_id,
            name=updated.name,
            color=updated.color,
            description=updated.description,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )
