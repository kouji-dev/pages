"""Remove label from issue use case."""

from uuid import UUID

import structlog

from src.domain.repositories import LabelRepository

logger = structlog.get_logger()


class RemoveLabelFromIssueUseCase:
    """Use case for removing a label from an issue."""

    def __init__(self, label_repository: LabelRepository) -> None:
        self._label_repository = label_repository

    async def execute(self, issue_id: str, label_id: str) -> None:
        """Remove a label from an issue."""
        logger.info("Removing label from issue", issue_id=issue_id, label_id=label_id)
        issue_uuid = UUID(issue_id)
        label_uuid = UUID(label_id)
        await self._label_repository.remove_label_from_issue(issue_uuid, label_uuid)
