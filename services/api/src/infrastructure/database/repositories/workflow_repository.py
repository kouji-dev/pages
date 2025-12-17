"""SQLAlchemy implementation of WorkflowRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.workflow import Workflow, WorkflowStatus, WorkflowTransition
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.workflow_repository import WorkflowRepository
from src.infrastructure.database.models.workflow import (
    WorkflowModel,
    WorkflowStatusModel,
    WorkflowTransitionModel,
)


class SQLAlchemyWorkflowRepository(WorkflowRepository):
    """SQLAlchemy implementation of WorkflowRepository.

    Adapts the domain WorkflowRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, workflow: Workflow) -> Workflow:
        """Create a new workflow in the database.

        Args:
            workflow: Workflow domain entity

        Returns:
            Created workflow with persisted data
        """
        # Create workflow model
        workflow_model = WorkflowModel(
            id=workflow.id,
            project_id=workflow.project_id,
            name=workflow.name,
            is_default=workflow.is_default,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
        )

        self._session.add(workflow_model)

        # Create status models
        for status in workflow.statuses:
            status_model = WorkflowStatusModel(
                id=status.id,
                workflow_id=status.workflow_id,
                name=status.name,
                order=status.order,
                is_initial=status.is_initial,
                is_final=status.is_final,
                created_at=status.created_at,
                updated_at=status.updated_at,
            )
            self._session.add(status_model)

        # Create transition models
        for transition in workflow.transitions:
            transition_model = WorkflowTransitionModel(
                id=transition.id,
                workflow_id=transition.workflow_id,
                from_status_id=transition.from_status_id,
                to_status_id=transition.to_status_id,
                name=transition.name,
                created_at=transition.created_at,
                updated_at=transition.updated_at,
            )
            self._session.add(transition_model)

        await self._session.flush()
        await self._session.refresh(workflow_model)

        # Reload with relationships
        reloaded = await self._get_by_id(workflow.id)
        if reloaded is None:
            raise RuntimeError("Failed to reload created workflow")
        return reloaded

    async def get_by_id(self, workflow_id: UUID) -> Workflow | None:
        """Get workflow by ID.

        Args:
            workflow_id: Workflow UUID

        Returns:
            Workflow if found, None otherwise
        """
        return await self._get_by_id(workflow_id)

    async def _get_by_id(self, workflow_id: UUID) -> Workflow | None:
        """Internal method to get workflow by ID with relationships.

        Args:
            workflow_id: Workflow UUID

        Returns:
            Workflow if found, None otherwise
        """
        result = await self._session.execute(
            select(WorkflowModel).where(WorkflowModel.id == workflow_id)
        )
        workflow_model = result.scalar_one_or_none()

        if workflow_model is None:
            return None

        return self._to_entity(workflow_model)

    async def get_by_project_id(self, project_id: UUID) -> list[Workflow]:
        """Get all workflows for a project.

        Args:
            project_id: Project UUID

        Returns:
            List of workflows for the project
        """
        result = await self._session.execute(
            select(WorkflowModel).where(WorkflowModel.project_id == project_id)
        )
        workflow_models = result.scalars().all()

        return [self._to_entity(model) for model in workflow_models]

    async def get_default_by_project_id(self, project_id: UUID) -> Workflow | None:
        """Get the default workflow for a project.

        Args:
            project_id: Project UUID

        Returns:
            Default workflow if found, None otherwise
        """
        result = await self._session.execute(
            select(WorkflowModel).where(
                WorkflowModel.project_id == project_id,
                WorkflowModel.is_default == True,  # noqa: E712
            )
        )
        workflow_model = result.scalar_one_or_none()

        if workflow_model is None:
            return None

        return self._to_entity(workflow_model)

    async def update(self, workflow: Workflow) -> Workflow:
        """Update an existing workflow.

        Args:
            workflow: Workflow entity with updated data

        Returns:
            Updated workflow

        Raises:
            EntityNotFoundException: If workflow not found
        """
        result = await self._session.execute(
            select(WorkflowModel).where(WorkflowModel.id == workflow.id)
        )
        workflow_model = result.scalar_one_or_none()

        if workflow_model is None:
            raise EntityNotFoundException("Workflow", str(workflow.id))

        # Update workflow fields
        workflow_model.name = workflow.name
        workflow_model.is_default = workflow.is_default
        workflow_model.updated_at = workflow.updated_at

        # Update statuses
        # First, get existing status IDs
        existing_status_ids = {s.id for s in workflow_model.statuses}
        new_status_ids = {s.id for s in workflow.statuses}

        # Delete removed statuses
        statuses_to_delete = [s for s in workflow_model.statuses if s.id not in new_status_ids]
        for status_model in statuses_to_delete:
            await self._session.delete(status_model)

        # Update or create statuses
        for status in workflow.statuses:
            if status.id in existing_status_ids:
                # Update existing
                status_model = next((s for s in workflow_model.statuses if s.id == status.id), None)
                if status_model:
                    status_model.name = status.name
                    status_model.order = status.order
                    status_model.is_initial = status.is_initial
                    status_model.is_final = status.is_final
                    status_model.updated_at = status.updated_at
            else:
                # Create new
                status_model = WorkflowStatusModel(
                    id=status.id,
                    workflow_id=status.workflow_id,
                    name=status.name,
                    order=status.order,
                    is_initial=status.is_initial,
                    is_final=status.is_final,
                    created_at=status.created_at,
                    updated_at=status.updated_at,
                )
                self._session.add(status_model)

        # Update transitions
        # First, get existing transition IDs
        existing_transition_ids = {t.id for t in workflow_model.transitions}
        new_transition_ids = {t.id for t in workflow.transitions}

        # Delete removed transitions
        transitions_to_delete = [
            t for t in workflow_model.transitions if t.id not in new_transition_ids
        ]
        for transition_model in transitions_to_delete:
            await self._session.delete(transition_model)

        # Update or create transitions
        for transition in workflow.transitions:
            if transition.id in existing_transition_ids:
                # Update existing
                transition_model = next(
                    (t for t in workflow_model.transitions if t.id == transition.id),
                    None,
                )
                if transition_model:
                    transition_model.from_status_id = transition.from_status_id
                    transition_model.to_status_id = transition.to_status_id
                    transition_model.name = transition.name
                    transition_model.updated_at = transition.updated_at
            else:
                # Create new
                transition_model = WorkflowTransitionModel(
                    id=transition.id,
                    workflow_id=transition.workflow_id,
                    from_status_id=transition.from_status_id,
                    to_status_id=transition.to_status_id,
                    name=transition.name,
                    created_at=transition.created_at,
                    updated_at=transition.updated_at,
                )
                self._session.add(transition_model)

        await self._session.flush()
        await self._session.refresh(workflow_model)

        # Reload with relationships
        reloaded = await self._get_by_id(workflow.id)
        if reloaded is None:
            raise RuntimeError("Failed to reload updated workflow")
        return reloaded

    async def delete(self, workflow_id: UUID) -> None:
        """Delete a workflow.

        Args:
            workflow_id: Workflow UUID

        Raises:
            EntityNotFoundException: If workflow not found
        """
        result = await self._session.execute(
            select(WorkflowModel).where(WorkflowModel.id == workflow_id)
        )
        workflow_model = result.scalar_one_or_none()

        if workflow_model is None:
            raise EntityNotFoundException("Workflow", str(workflow_id))

        await self._session.delete(workflow_model)
        await self._session.flush()

    async def exists_by_id(self, workflow_id: UUID) -> bool:
        """Check if a workflow exists.

        Args:
            workflow_id: Workflow UUID

        Returns:
            True if workflow exists, False otherwise
        """
        result = await self._session.execute(
            select(WorkflowModel).where(WorkflowModel.id == workflow_id)
        )
        return result.scalar_one_or_none() is not None

    def _to_entity(self, model: WorkflowModel) -> Workflow:
        """Convert WorkflowModel to Workflow entity.

        Args:
            model: WorkflowModel instance

        Returns:
            Workflow domain entity
        """
        # Convert statuses
        statuses = [
            WorkflowStatus(
                id=s.id,
                workflow_id=s.workflow_id,
                name=s.name,
                order=s.order,
                is_initial=s.is_initial,
                is_final=s.is_final,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in model.statuses
        ]

        # Convert transitions
        transitions = [
            WorkflowTransition(
                id=t.id,
                workflow_id=t.workflow_id,
                from_status_id=t.from_status_id,
                to_status_id=t.to_status_id,
                name=t.name,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in model.transitions
        ]

        return Workflow(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            is_default=model.is_default,
            created_at=model.created_at,
            updated_at=model.updated_at,
            statuses=statuses,
            transitions=transitions,
        )
