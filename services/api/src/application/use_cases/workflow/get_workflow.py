"""Get workflow use case."""

from uuid import UUID

import structlog

from src.application.dtos.workflow import WorkflowResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import WorkflowRepository

logger = structlog.get_logger()


class GetWorkflowUseCase:
    """Use case for getting a workflow."""

    def __init__(self, workflow_repository: WorkflowRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            workflow_repository: Workflow repository for data access
        """
        self._workflow_repository = workflow_repository

    async def execute(self, workflow_id: UUID) -> WorkflowResponse:
        """Execute get workflow.

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow response DTO

        Raises:
            EntityNotFoundException: If workflow not found
        """
        logger.info("Getting workflow", workflow_id=str(workflow_id))

        workflow = await self._workflow_repository.get_by_id(workflow_id)

        if workflow is None:
            logger.warning("Workflow not found", workflow_id=str(workflow_id))
            raise EntityNotFoundException("Workflow", str(workflow_id))

        # Convert to response DTO
        return WorkflowResponse.model_validate(
            {
                "id": workflow.id,
                "project_id": workflow.project_id,
                "name": workflow.name,
                "is_default": workflow.is_default,
                "created_at": workflow.created_at,
                "updated_at": workflow.updated_at,
                "statuses": [
                    {
                        "id": s.id,
                        "workflow_id": s.workflow_id,
                        "name": s.name,
                        "order": s.order,
                        "is_initial": s.is_initial,
                        "is_final": s.is_final,
                        "created_at": s.created_at,
                        "updated_at": s.updated_at,
                    }
                    for s in workflow.statuses
                ],
                "transitions": [
                    {
                        "id": t.id,
                        "workflow_id": t.workflow_id,
                        "from_status_id": t.from_status_id,
                        "to_status_id": t.to_status_id,
                        "name": t.name,
                        "created_at": t.created_at,
                        "updated_at": t.updated_at,
                    }
                    for t in workflow.transitions
                ],
            }
        )
