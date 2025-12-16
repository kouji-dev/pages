"""Remove issue from sprint use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import SprintRepository

logger = structlog.get_logger()


class RemoveIssueFromSprintUseCase:
    """Use case for removing an issue from a sprint."""

    def __init__(self, sprint_repository: SprintRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            sprint_repository: Sprint repository
        """
        self._sprint_repository = sprint_repository

    async def execute(
        self,
        sprint_id: UUID,
        issue_id: UUID,
    ) -> None:
        """Execute removing issue from sprint.

        Args:
            sprint_id: Sprint UUID
            issue_id: Issue UUID

        Raises:
            EntityNotFoundException: If sprint or issue not found, or issue not in sprint
        """
        logger.info(
            "Removing issue from sprint",
            sprint_id=str(sprint_id),
            issue_id=str(issue_id),
        )

        # Verify sprint exists
        sprint = await self._sprint_repository.get_by_id(sprint_id)
        if sprint is None:
            logger.warning("Sprint not found", sprint_id=str(sprint_id))
            raise EntityNotFoundException("Sprint", str(sprint_id))

        # Remove issue from sprint
        await self._sprint_repository.remove_issue_from_sprint(sprint_id, issue_id)

        logger.info(
            "Issue removed from sprint successfully",
            sprint_id=str(sprint_id),
            issue_id=str(issue_id),
        )
