"""Delete workflow use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import WorkflowRepository

logger = structlog.get_logger()


class DeleteWorkflowUseCase:
    """Use case for deleting a workflow."""

    def __init__(self, workflow_repository: WorkflowRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            workflow_repository: Workflow repository for data access
        """
        self._workflow_repository = workflow_repository

    async def execute(self, workflow_id: UUID) -> None:
        """Execute delete workflow.

        Args:
            workflow_id: Workflow ID

        Raises:
            EntityNotFoundException: If workflow not found
        """
        logger.info("Deleting workflow", workflow_id=str(workflow_id))

        # Verify workflow exists
        workflow = await self._workflow_repository.get_by_id(workflow_id)
        if workflow is None:
            logger.warning("Workflow not found for deletion", workflow_id=str(workflow_id))
            raise EntityNotFoundException("Workflow", str(workflow_id))

        await self._workflow_repository.delete(workflow_id)

        logger.info("Workflow deleted", workflow_id=str(workflow_id))
