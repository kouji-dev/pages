"""Workflow repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.workflow import Workflow


class WorkflowRepository(ABC):
    """Abstract workflow repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, workflow: Workflow) -> Workflow:
        """Create a new workflow.

        Args:
            workflow: Workflow entity to create

        Returns:
            Created workflow with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, workflow_id: UUID) -> Workflow | None:
        """Get workflow by ID.

        Args:
            workflow_id: Workflow UUID

        Returns:
            Workflow if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_project_id(self, project_id: UUID) -> list[Workflow]:
        """Get all workflows for a project.

        Args:
            project_id: Project UUID

        Returns:
            List of workflows for the project
        """
        ...

    @abstractmethod
    async def get_default_by_project_id(self, project_id: UUID) -> Workflow | None:
        """Get the default workflow for a project.

        Args:
            project_id: Project UUID

        Returns:
            Default workflow if found, None otherwise
        """
        ...

    @abstractmethod
    async def update(self, workflow: Workflow) -> Workflow:
        """Update an existing workflow.

        Args:
            workflow: Workflow entity with updated data

        Returns:
            Updated workflow

        Raises:
            EntityNotFoundException: If workflow not found
        """
        ...

    @abstractmethod
    async def delete(self, workflow_id: UUID) -> None:
        """Delete a workflow.

        Args:
            workflow_id: Workflow UUID

        Raises:
            EntityNotFoundException: If workflow not found
        """
        ...

    @abstractmethod
    async def exists_by_id(self, workflow_id: UUID) -> bool:
        """Check if a workflow exists.

        Args:
            workflow_id: Workflow UUID

        Returns:
            True if workflow exists, False otherwise
        """
        ...
