"""Create workflow use case."""

from uuid import UUID

import structlog

from src.application.dtos.workflow import CreateWorkflowRequest, WorkflowResponse
from src.domain.entities.workflow import Workflow
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import ProjectRepository, WorkflowRepository

logger = structlog.get_logger()


class CreateWorkflowUseCase:
    """Use case for creating a workflow."""

    def __init__(
        self,
        workflow_repository: WorkflowRepository,
        project_repository: ProjectRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            workflow_repository: Workflow repository for data access
            project_repository: Project repository to verify project exists
        """
        self._workflow_repository = workflow_repository
        self._project_repository = project_repository

    async def execute(self, project_id: UUID, request: CreateWorkflowRequest) -> WorkflowResponse:
        """Execute create workflow.

        Args:
            project_id: Project ID
            request: Workflow creation request

        Returns:
            Created workflow response DTO

        Raises:
            EntityNotFoundException: If project not found
            ValidationException: If workflow data is invalid
        """
        logger.info("Creating workflow", project_id=str(project_id), name=request.name)

        # Verify project exists
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            logger.warning("Project not found for workflow creation", project_id=str(project_id))
            raise EntityNotFoundException("Project", str(project_id))

        # Create workflow entity
        try:
            workflow = Workflow.create(
                project_id=project_id,
                name=request.name,
                is_default=request.is_default,
            )
        except ValueError as e:
            raise ValidationException(str(e), field="name") from e

        # Add statuses
        for status_req in request.statuses:
            try:
                workflow.add_status(
                    name=status_req.name,
                    order=status_req.order,
                    is_initial=status_req.is_initial,
                    is_final=status_req.is_final,
                )
            except ValueError as e:
                raise ValidationException(str(e), field="statuses") from e

        # Add transitions
        for transition_req in request.transitions:
            try:
                workflow.add_transition(
                    from_status_id=transition_req.from_status_id,
                    to_status_id=transition_req.to_status_id,
                    name=transition_req.name,
                )
            except ValueError as e:
                raise ValidationException(str(e), field="transitions") from e

        # Validate workflow structure
        try:
            workflow.validate()
        except ValueError as e:
            raise ValidationException(str(e), field="workflow") from e

        # If this is set as default, unset other defaults
        if request.is_default:
            existing_default = await self._workflow_repository.get_default_by_project_id(project_id)
            if existing_default:
                existing_default.set_default(False)
                await self._workflow_repository.update(existing_default)

        # Save to database
        created_workflow = await self._workflow_repository.create(workflow)

        logger.info("Workflow created", workflow_id=str(created_workflow.id))

        # Convert to response DTO
        return WorkflowResponse.model_validate(
            {
                "id": created_workflow.id,
                "project_id": created_workflow.project_id,
                "name": created_workflow.name,
                "is_default": created_workflow.is_default,
                "created_at": created_workflow.created_at,
                "updated_at": created_workflow.updated_at,
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
                    for s in created_workflow.statuses
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
                    for t in created_workflow.transitions
                ],
            }
        )
