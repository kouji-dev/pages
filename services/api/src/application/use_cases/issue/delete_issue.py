"""Delete issue use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import IssueActivityRepository, IssueRepository

logger = structlog.get_logger()


class DeleteIssueUseCase:
    """Use case for deleting an issue (soft delete)."""

    def __init__(
        self,
        issue_repository: IssueRepository,
        activity_repository: IssueActivityRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            issue_repository: Issue repository for data access
            activity_repository: Issue activity repository for logging
        """
        self._issue_repository = issue_repository
        self._activity_repository = activity_repository

    async def execute(self, issue_id: str, user_id: UUID | None = None) -> None:
        """Execute delete issue.

        Args:
            issue_id: Issue ID

        Raises:
            EntityNotFoundException: If issue not found
        """
        logger.info("Deleting issue", issue_id=issue_id)

        issue_uuid = UUID(issue_id)
        issue = await self._issue_repository.get_by_id(issue_uuid)

        if issue is None:
            logger.warning("Issue not found for deletion", issue_id=issue_id)
            raise EntityNotFoundException("Issue", issue_id)

        issue.delete()  # Soft delete
        await self._issue_repository.update(issue)

        # Create activity log for issue deletion
        await self._activity_repository.create(
            issue_id=issue.id,
            user_id=user_id,
            action="deleted",
        )

        logger.info("Issue soft-deleted", issue_id=issue_id)

