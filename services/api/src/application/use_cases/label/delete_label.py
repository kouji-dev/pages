"""Delete label use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import LabelRepository

logger = structlog.get_logger()


class DeleteLabelUseCase:
    """Use case for deleting a label."""

    def __init__(self, label_repository: LabelRepository) -> None:
        self._label_repository = label_repository

    async def execute(self, label_id: str) -> None:
        """Delete a label (cascade to issue_labels)."""
        logger.info("Deleting label", label_id=label_id)
        label_uuid = UUID(label_id)
        label = await self._label_repository.get_by_id(label_uuid)
        if label is None:
            raise EntityNotFoundException("Label", label_id)
        await self._label_repository.delete(label_uuid)
