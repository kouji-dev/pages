"""Workflow domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4


@dataclass
class WorkflowStatus:
    """Workflow status entity.

    Represents a status within a workflow (e.g., "To Do", "In Progress", "Done").
    """

    id: UUID
    workflow_id: UUID
    name: str
    order: int
    is_initial: bool = False
    is_final: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate workflow status."""
        if not self.name or not self.name.strip():
            raise ValueError("Workflow status name cannot be empty")

        self.name = self.name.strip()

        if len(self.name) > 100:
            raise ValueError("Workflow status name cannot exceed 100 characters")

        if self.order < 0:
            raise ValueError("Workflow status order must be non-negative")

    @classmethod
    def create(
        cls,
        workflow_id: UUID,
        name: str,
        order: int,
        is_initial: bool = False,
        is_final: bool = False,
    ) -> Self:
        """Create a new workflow status.

        Args:
            workflow_id: ID of the workflow this status belongs to
            name: Status name
            order: Display order
            is_initial: Whether this is the initial status
            is_final: Whether this is a final status

        Returns:
            New WorkflowStatus instance
        """
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            workflow_id=workflow_id,
            name=name,
            order=order,
            is_initial=is_initial,
            is_final=is_final,
            created_at=now,
            updated_at=now,
        )

    def update_name(self, name: str) -> None:
        """Update status name.

        Args:
            name: New status name

        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.strip():
            raise ValueError("Workflow status name cannot be empty")

        name = name.strip()

        if len(name) > 100:
            raise ValueError("Workflow status name cannot exceed 100 characters")

        self.name = name
        self._touch()

    def update_order(self, order: int) -> None:
        """Update status order.

        Args:
            order: New order

        Raises:
            ValueError: If order is invalid
        """
        if order < 0:
            raise ValueError("Workflow status order must be non-negative")

        self.order = order
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


@dataclass
class WorkflowTransition:
    """Workflow transition entity.

    Represents a valid transition between two statuses in a workflow.
    """

    id: UUID
    workflow_id: UUID
    from_status_id: UUID
    to_status_id: UUID
    name: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate workflow transition."""
        if self.from_status_id == self.to_status_id:
            raise ValueError("Transition cannot have same from and to status")

        if self.name and len(self.name) > 100:
            raise ValueError("Transition name cannot exceed 100 characters")

    @classmethod
    def create(
        cls,
        workflow_id: UUID,
        from_status_id: UUID,
        to_status_id: UUID,
        name: str | None = None,
    ) -> Self:
        """Create a new workflow transition.

        Args:
            workflow_id: ID of the workflow this transition belongs to
            from_status_id: Source status ID
            to_status_id: Target status ID
            name: Optional transition name

        Returns:
            New WorkflowTransition instance

        Raises:
            ValueError: If transition is invalid
        """
        if from_status_id == to_status_id:
            raise ValueError("Transition cannot have same from and to status")

        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            workflow_id=workflow_id,
            from_status_id=from_status_id,
            to_status_id=to_status_id,
            name=name,
            created_at=now,
            updated_at=now,
        )

    def update_name(self, name: str | None) -> None:
        """Update transition name.

        Args:
            name: New transition name (can be None)

        Raises:
            ValueError: If name is invalid
        """
        if name and len(name) > 100:
            raise ValueError("Transition name cannot exceed 100 characters")

        self.name = name
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


@dataclass
class Workflow:
    """Workflow domain entity.

    Represents a custom workflow for managing issue status transitions.
    This is an aggregate root in DDD terms.
    """

    id: UUID
    project_id: UUID
    name: str
    is_default: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Aggregated entities (not stored directly, loaded via repository)
    statuses: list[WorkflowStatus] = field(default_factory=list)
    transitions: list[WorkflowTransition] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate workflow."""
        if not self.name or not self.name.strip():
            raise ValueError("Workflow name cannot be empty")

        self.name = self.name.strip()

        if len(self.name) > 100:
            raise ValueError("Workflow name cannot exceed 100 characters")

    @classmethod
    def create(
        cls,
        project_id: UUID,
        name: str,
        is_default: bool = False,
    ) -> Self:
        """Create a new workflow.

        Factory method for creating new workflows.

        Args:
            project_id: ID of the project this workflow belongs to
            name: Workflow name
            is_default: Whether this is the default workflow for the project

        Returns:
            New Workflow instance

        Raises:
            ValueError: If name is invalid
        """
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            project_id=project_id,
            name=name,
            is_default=is_default,
            created_at=now,
            updated_at=now,
            statuses=[],
            transitions=[],
        )

    def update_name(self, name: str) -> None:
        """Update workflow name.

        Args:
            name: New workflow name

        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.strip():
            raise ValueError("Workflow name cannot be empty")

        name = name.strip()

        if len(name) > 100:
            raise ValueError("Workflow name cannot exceed 100 characters")

        self.name = name
        self._touch()

    def set_default(self, is_default: bool) -> None:
        """Set whether this workflow is the default.

        Args:
            is_default: Whether this is the default workflow
        """
        self.is_default = is_default
        self._touch()

    def add_status(
        self,
        name: str,
        order: int,
        is_initial: bool = False,
        is_final: bool = False,
    ) -> WorkflowStatus:
        """Add a status to this workflow.

        Args:
            name: Status name
            order: Display order
            is_initial: Whether this is the initial status
            is_final: Whether this is a final status

        Returns:
            Created WorkflowStatus instance
        """
        status = WorkflowStatus.create(
            workflow_id=self.id,
            name=name,
            order=order,
            is_initial=is_initial,
            is_final=is_final,
        )
        self.statuses.append(status)
        self._touch()
        return status

    def remove_status(self, status_id: UUID) -> None:
        """Remove a status from this workflow.

        Args:
            status_id: ID of the status to remove

        Raises:
            ValueError: If status not found or has transitions
        """
        # Find status
        status = next((s for s in self.statuses if s.id == status_id), None)
        if status is None:
            raise ValueError(f"Status {status_id} not found in workflow")

        # Check if status has any transitions
        has_transitions = any(
            t.from_status_id == status_id or t.to_status_id == status_id for t in self.transitions
        )
        if has_transitions:
            raise ValueError(
                f"Cannot remove status {status_id} because it has transitions. Remove transitions first."
            )

        self.statuses.remove(status)
        self._touch()

    def add_transition(
        self,
        from_status_id: UUID,
        to_status_id: UUID,
        name: str | None = None,
    ) -> WorkflowTransition:
        """Add a transition to this workflow.

        Args:
            from_status_id: Source status ID
            to_status_id: Target status ID
            name: Optional transition name

        Returns:
            Created WorkflowTransition instance

        Raises:
            ValueError: If transition is invalid or statuses not found
        """
        # Verify statuses exist
        from_status = next((s for s in self.statuses if s.id == from_status_id), None)
        to_status = next((s for s in self.statuses if s.id == to_status_id), None)

        if from_status is None:
            raise ValueError(f"From status {from_status_id} not found in workflow")
        if to_status is None:
            raise ValueError(f"To status {to_status_id} not found in workflow")

        # Check for duplicate transition
        existing = next(
            (
                t
                for t in self.transitions
                if t.from_status_id == from_status_id and t.to_status_id == to_status_id
            ),
            None,
        )
        if existing:
            raise ValueError(f"Transition from {from_status_id} to {to_status_id} already exists")

        transition = WorkflowTransition.create(
            workflow_id=self.id,
            from_status_id=from_status_id,
            to_status_id=to_status_id,
            name=name,
        )
        self.transitions.append(transition)
        self._touch()
        return transition

    def remove_transition(self, transition_id: UUID) -> None:
        """Remove a transition from this workflow.

        Args:
            transition_id: ID of the transition to remove

        Raises:
            ValueError: If transition not found
        """
        transition = next((t for t in self.transitions if t.id == transition_id), None)
        if transition is None:
            raise ValueError(f"Transition {transition_id} not found in workflow")

        self.transitions.remove(transition)
        self._touch()

    def get_initial_status(self) -> WorkflowStatus | None:
        """Get the initial status of this workflow.

        Returns:
            Initial status if found, None otherwise
        """
        return next((s for s in self.statuses if s.is_initial), None)

    def get_final_statuses(self) -> list[WorkflowStatus]:
        """Get all final statuses of this workflow.

        Returns:
            List of final statuses
        """
        return [s for s in self.statuses if s.is_final]

    def is_valid_transition(self, from_status_id: UUID, to_status_id: UUID) -> bool:
        """Check if a transition is valid.

        Args:
            from_status_id: Source status ID
            to_status_id: Target status ID

        Returns:
            True if transition is valid, False otherwise
        """
        return any(
            t.from_status_id == from_status_id and t.to_status_id == to_status_id
            for t in self.transitions
        )

    def get_valid_transitions(self, from_status_id: UUID) -> list[WorkflowTransition]:
        """Get all valid transitions from a status.

        Args:
            from_status_id: Source status ID

        Returns:
            List of valid transitions from the status
        """
        return [t for t in self.transitions if t.from_status_id == from_status_id]

    def validate(self) -> None:
        """Validate workflow structure.

        Raises:
            ValueError: If workflow is invalid
        """
        if not self.statuses:
            raise ValueError("Workflow must have at least one status")

        # Check for exactly one initial status
        initial_statuses = [s for s in self.statuses if s.is_initial]
        if len(initial_statuses) != 1:
            raise ValueError("Workflow must have exactly one initial status")

        # Check for at least one final status
        final_statuses = [s for s in self.statuses if s.is_final]
        if not final_statuses:
            raise ValueError("Workflow must have at least one final status")

        # Check that all transitions reference valid statuses
        status_ids = {s.id for s in self.statuses}
        for transition in self.transitions:
            if transition.from_status_id not in status_ids:
                raise ValueError(f"Transition {transition.id} references invalid from_status_id")
            if transition.to_status_id not in status_ids:
                raise ValueError(f"Transition {transition.id} references invalid to_status_id")

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
