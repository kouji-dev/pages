"""Validate transition use case."""

from uuid import UUID

import structlog

from src.application.dtos.workflow import ValidateTransitionRequest, ValidateTransitionResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import WorkflowRepository

logger = structlog.get_logger()


class ValidateTransitionUseCase:
    """Use case for validating a workflow transition."""

    def __init__(self, workflow_repository: WorkflowRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            workflow_repository: Workflow repository for data access
        """
        self._workflow_repository = workflow_repository

    async def execute(
        self, workflow_id: UUID, request: ValidateTransitionRequest
    ) -> ValidateTransitionResponse:
        """Execute validate transition.

        Args:
            workflow_id: Workflow ID
            request: Transition validation request

        Returns:
            Validation response DTO

        Raises:
            EntityNotFoundException: If workflow not found
        """
        logger.info(
            "Validating transition",
            workflow_id=str(workflow_id),
            from_status_id=str(request.from_status_id),
            to_status_id=str(request.to_status_id),
        )

        workflow = await self._workflow_repository.get_by_id(workflow_id)

        if workflow is None:
            logger.warning("Workflow not found", workflow_id=str(workflow_id))
            raise EntityNotFoundException("Workflow", str(workflow_id))

        # Check if transition is valid
        is_valid = workflow.is_valid_transition(request.from_status_id, request.to_status_id)

        message = None
        if not is_valid:
            message = (
                f"Transition from status {request.from_status_id} "
                f"to status {request.to_status_id} is not allowed in this workflow"
            )

        return ValidateTransitionResponse(is_valid=is_valid, message=message)
