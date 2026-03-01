"""List issue labels use case."""

from uuid import UUID

import structlog

from src.application.dtos.label import LabelResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import IssueRepository, LabelRepository

logger = structlog.get_logger()


class ListIssueLabelsUseCase:
    """Use case for listing labels of an issue."""

    def __init__(
        self,
        label_repository: LabelRepository,
        issue_repository: IssueRepository,
    ) -> None:
        self._label_repository = label_repository
        self._issue_repository = issue_repository

    async def execute(self, issue_id: str) -> list[LabelResponse]:
        """List all labels attached to an issue."""
        logger.info("Listing issue labels", issue_id=issue_id)
        issue_uuid = UUID(issue_id)
        issue = await self._issue_repository.get_by_id(issue_uuid)
        if issue is None:
            raise EntityNotFoundException("Issue", issue_id)
        labels = await self._label_repository.get_labels_for_issue(issue_uuid)
        return [
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
        ]
