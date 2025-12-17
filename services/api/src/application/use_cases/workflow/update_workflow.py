"""Update workflow use case."""

from uuid import UUID

import structlog

from src.application.dtos.workflow import UpdateWorkflowRequest, WorkflowResponse
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import WorkflowRepository

logger = structlog.get_logger()


class UpdateWorkflowUseCase:
    """Use case for updating a workflow."""

    def __init__(self, workflow_repository: WorkflowRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            workflow_repository: Workflow repository for data access
        """
        self._workflow_repository = workflow_repository

    async def execute(self, workflow_id: UUID, request: UpdateWorkflowRequest) -> WorkflowResponse:
        """Execute update workflow.

        Args:
            workflow_id: Workflow ID
            request: Workflow update request

        Returns:
            Updated workflow response DTO

        Raises:
            EntityNotFoundException: If workflow not found
            ValidationException: If workflow data is invalid
        """
        logger.info("Updating workflow", workflow_id=str(workflow_id))

        workflow = await self._workflow_repository.get_by_id(workflow_id)

        if workflow is None:
            logger.warning("Workflow not found for update", workflow_id=str(workflow_id))
            raise EntityNotFoundException("Workflow", str(workflow_id))

        # Apply updates
        if request.name is not None:
            try:
                workflow.update_name(request.name)
            except ValueError as e:
                raise ValidationException(str(e), field="name") from e

        if request.is_default is not None:
            # If setting as default, unset other defaults
            if request.is_default:
                existing_default = await self._workflow_repository.get_default_by_project_id(
                    workflow.project_id
                )
                if existing_default and existing_default.id != workflow_id:
                    existing_default.set_default(False)
                    await self._workflow_repository.update(existing_default)

            workflow.set_default(request.is_default)

        # Save to database
        updated_workflow = await self._workflow_repository.update(workflow)

        logger.info("Workflow updated", workflow_id=str(workflow_id))

        # Convert to response DTO
        return WorkflowResponse.model_validate(
            {
                "id": updated_workflow.id,
                "project_id": updated_workflow.project_id,
                "name": updated_workflow.name,
                "is_default": updated_workflow.is_default,
                "created_at": updated_workflow.created_at,
                "updated_at": updated_workflow.updated_at,
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
                    for s in updated_workflow.statuses
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
                    for t in updated_workflow.transitions
                ],
            }
        )
