"""Add label to issue use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import IssueRepository, LabelRepository

logger = structlog.get_logger()


class AddLabelToIssueUseCase:
    """Use case for adding a label to an issue."""

    def __init__(
        self,
        label_repository: LabelRepository,
        issue_repository: IssueRepository,
    ) -> None:
        self._label_repository = label_repository
        self._issue_repository = issue_repository

    async def execute(self, issue_id: str, label_id: str) -> None:
        """Add a label to an issue."""
        logger.info("Adding label to issue", issue_id=issue_id, label_id=label_id)
        issue_uuid = UUID(issue_id)
        label_uuid = UUID(label_id)
        issue = await self._issue_repository.get_by_id(issue_uuid)
        if issue is None:
            raise EntityNotFoundException("Issue", issue_id)
        await self._label_repository.add_label_to_issue(issue_uuid, label_uuid)
