"""Delete sprint use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import SprintRepository

logger = structlog.get_logger()


class DeleteSprintUseCase:
    """Use case for deleting a sprint."""

    def __init__(self, sprint_repository: SprintRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            sprint_repository: Sprint repository
        """
        self._sprint_repository = sprint_repository

    async def execute(self, sprint_id: UUID) -> None:
        """Execute sprint deletion.

        Args:
            sprint_id: Sprint UUID

        Raises:
            EntityNotFoundException: If sprint not found
        """
        logger.info("Deleting sprint", sprint_id=str(sprint_id))

        # Verify sprint exists
        sprint = await self._sprint_repository.get_by_id(sprint_id)
        if sprint is None:
            logger.warning("Sprint not found", sprint_id=str(sprint_id))
            raise EntityNotFoundException("Sprint", str(sprint_id))

        # Delete sprint (hard delete)
        await self._sprint_repository.delete(sprint_id)

        logger.info("Sprint deleted successfully", sprint_id=str(sprint_id))
