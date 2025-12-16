"""Reorder sprint issues use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import SprintRepository

logger = structlog.get_logger()


class ReorderSprintIssuesUseCase:
    """Use case for reordering issues within a sprint."""

    def __init__(self, sprint_repository: SprintRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            sprint_repository: Sprint repository
        """
        self._sprint_repository = sprint_repository

    async def execute(
        self,
        sprint_id: UUID,
        issue_orders: dict[UUID, int],
    ) -> None:
        """Execute reordering sprint issues.

        Args:
            sprint_id: Sprint UUID
            issue_orders: Dictionary mapping issue IDs to their new order

        Raises:
            EntityNotFoundException: If sprint not found
        """
        logger.info(
            "Reordering sprint issues",
            sprint_id=str(sprint_id),
            issue_count=len(issue_orders),
        )

        # Verify sprint exists
        sprint = await self._sprint_repository.get_by_id(sprint_id)
        if sprint is None:
            logger.warning("Sprint not found", sprint_id=str(sprint_id))
            raise EntityNotFoundException("Sprint", str(sprint_id))

        # Reorder issues
        await self._sprint_repository.reorder_sprint_issues(sprint_id, issue_orders)

        logger.info(
            "Sprint issues reordered successfully",
            sprint_id=str(sprint_id),
        )
