"""List workflows use case."""

from uuid import UUID

import structlog

from src.application.dtos.workflow import WorkflowListItemResponse, WorkflowListResponse
from src.domain.repositories import WorkflowRepository

logger = structlog.get_logger()


class ListWorkflowsUseCase:
    """Use case for listing workflows."""

    def __init__(self, workflow_repository: WorkflowRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            workflow_repository: Workflow repository for data access
        """
        self._workflow_repository = workflow_repository

    async def execute(self, project_id: UUID) -> WorkflowListResponse:
        """Execute list workflows.

        Args:
            project_id: Project ID

        Returns:
            Workflow list response DTO
        """
        logger.info("Listing workflows", project_id=str(project_id))

        workflows = await self._workflow_repository.get_by_project_id(project_id)

        # Convert to response DTOs
        workflow_items = [
            WorkflowListItemResponse.model_validate(
                {
                    "id": w.id,
                    "project_id": w.project_id,
                    "name": w.name,
                    "is_default": w.is_default,
                    "created_at": w.created_at,
                    "updated_at": w.updated_at,
                }
            )
            for w in workflows
        ]

        return WorkflowListResponse(workflows=workflow_items, total=len(workflow_items))
