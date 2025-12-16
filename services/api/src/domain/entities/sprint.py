"""Sprint domain entity."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Self
from uuid import UUID, uuid4

from src.domain.value_objects.sprint_status import SprintStatus


@dataclass
class Sprint:
    """Sprint domain entity.

    Represents a sprint within a project.
    This is an aggregate root in DDD terms.
    """

    id: UUID
    project_id: UUID
    name: str
    goal: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: SprintStatus = SprintStatus.PLANNED
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate sprint entity."""
        if not self.name or not self.name.strip():
            raise ValueError("Sprint name cannot be empty")

        self.name = self.name.strip()

        if len(self.name) > 255:
            raise ValueError("Sprint name cannot exceed 255 characters")

        if self.goal and len(self.goal) > 1000:
            raise ValueError("Sprint goal cannot exceed 1000 characters")

        # Validate dates
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValueError("Sprint start date must be before end date")

    @classmethod
    def create(
        cls,
        project_id: UUID,
        name: str,
        goal: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        status: SprintStatus = SprintStatus.PLANNED,
    ) -> Self:
        """Create a new sprint.

        Factory method for creating new sprints with proper defaults.

        Args:
            project_id: The ID of the project this sprint belongs to
            name: Sprint name
            goal: Optional sprint goal
            start_date: Optional sprint start date
            end_date: Optional sprint end date
            status: Sprint status (default: PLANNED)

        Returns:
            New Sprint instance

        Raises:
            ValueError: If name or dates are invalid
        """
        now = datetime.utcnow()

        sprint = cls(
            id=uuid4(),
            project_id=project_id,
            name=name,
            goal=goal,
            start_date=start_date,
            end_date=end_date,
            status=status,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        return sprint

    def update_name(self, name: str) -> None:
        """Update sprint name.

        Args:
            name: New sprint name

        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.strip():
            raise ValueError("Sprint name cannot be empty")

        name = name.strip()

        if len(name) > 255:
            raise ValueError("Sprint name cannot exceed 255 characters")

        self.name = name
        self._touch()

    def update_goal(self, goal: str | None) -> None:
        """Update sprint goal.

        Args:
            goal: New sprint goal (can be None)

        Raises:
            ValueError: If goal is too long
        """
        if goal and len(goal) > 1000:
            raise ValueError("Sprint goal cannot exceed 1000 characters")

        self.goal = goal
        self._touch()

    def update_dates(self, start_date: date | None, end_date: date | None) -> None:
        """Update sprint dates.

        Args:
            start_date: New start date (can be None)
            end_date: New end date (can be None)

        Raises:
            ValueError: If dates are invalid
        """
        if start_date and end_date:
            if start_date >= end_date:
                raise ValueError("Sprint start date must be before end date")

        self.start_date = start_date
        self.end_date = end_date
        self._touch()

    def update_status(self, status: SprintStatus) -> None:
        """Update sprint status.

        Args:
            status: New sprint status
        """
        self.status = status
        self._touch()

    def is_active(self) -> bool:
        """Check if sprint is active.

        Returns:
            True if sprint status is ACTIVE, False otherwise
        """
        return self.status == SprintStatus.ACTIVE

    def is_completed(self) -> bool:
        """Check if sprint is completed.

        Returns:
            True if sprint status is COMPLETED, False otherwise
        """
        return self.status == SprintStatus.COMPLETED

    def is_planned(self) -> bool:
        """Check if sprint is planned.

        Returns:
            True if sprint status is PLANNED, False otherwise
        """
        return self.status == SprintStatus.PLANNED

    def delete(self) -> None:
        """Soft delete sprint by setting deleted_at timestamp."""
        self.deleted_at = datetime.utcnow()
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
