"""Get label use case."""

from uuid import UUID

import structlog

from src.application.dtos.label import LabelResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import LabelRepository

logger = structlog.get_logger()


class GetLabelUseCase:
    """Use case for retrieving a label by ID."""

    def __init__(self, label_repository: LabelRepository) -> None:
        self._label_repository = label_repository

    async def execute(self, label_id: str) -> LabelResponse:
        """Get label by ID."""
        logger.info("Getting label", label_id=label_id)
        label_uuid = UUID(label_id)
        label = await self._label_repository.get_by_id(label_uuid)
        if label is None:
            raise EntityNotFoundException("Label", label_id)
        return LabelResponse(
            id=label.id,
            project_id=label.project_id,
            name=label.name,
            color=label.color,
            description=label.description,
            created_at=label.created_at,
            updated_at=label.updated_at,
        )
