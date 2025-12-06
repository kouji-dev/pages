"""Issue domain entity."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Self
from uuid import UUID, uuid4


@dataclass
class Issue:
    """Issue domain entity.

    Represents an issue (task, bug, story) within a project.
    This is an aggregate root in DDD terms.
    """

    id: UUID
    project_id: UUID
    issue_number: int
    title: str
    description: str | None = None
    type: str = "task"  # task, bug, story, epic
    status: str = "todo"  # todo, in_progress, done, cancelled
    priority: str = "medium"  # low, medium, high, critical
    reporter_id: UUID | None = None
    assignee_id: UUID | None = None
    due_date: date | None = None
    story_points: int | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate issue entity."""
        if not self.title or not self.title.strip():
            raise ValueError("Issue title cannot be empty")

        self.title = self.title.strip()

        if len(self.title) > 255:
            raise ValueError("Issue title cannot exceed 255 characters")

        if self.issue_number < 1:
            raise ValueError("Issue number must be positive")

        # Validate type
        valid_types = {"task", "bug", "story", "epic"}
        if self.type not in valid_types:
            raise ValueError(f"Issue type must be one of: {', '.join(valid_types)}")

        # Validate status
        valid_statuses = {"todo", "in_progress", "done", "cancelled"}
        if self.status not in valid_statuses:
            raise ValueError(f"Issue status must be one of: {', '.join(valid_statuses)}")

        # Validate priority
        valid_priorities = {"low", "medium", "high", "critical"}
        if self.priority not in valid_priorities:
            raise ValueError(f"Issue priority must be one of: {', '.join(valid_priorities)}")

        if self.story_points is not None and self.story_points < 0:
            raise ValueError("Story points cannot be negative")

    @classmethod
    def create(
        cls,
        project_id: UUID,
        issue_number: int,
        title: str,
        description: str | None = None,
        type: str = "task",
        status: str = "todo",
        priority: str = "medium",
        reporter_id: UUID | None = None,
        assignee_id: UUID | None = None,
        due_date: date | None = None,
        story_points: int | None = None,
    ) -> Self:
        """Create a new issue.

        Factory method for creating new issues with proper defaults.

        Args:
            project_id: The ID of the project this issue belongs to
            issue_number: Auto-incremented issue number within the project
            title: Issue title
            description: Optional issue description
            type: Issue type (task, bug, story, epic)
            status: Issue status (todo, in_progress, done, cancelled)
            priority: Issue priority (low, medium, high, critical)
            reporter_id: ID of the user who reported the issue
            assignee_id: ID of the user assigned to the issue
            due_date: Optional due date
            story_points: Optional story points estimation

        Returns:
            New Issue instance

        Raises:
            ValueError: If title or other fields are invalid
        """
        now = datetime.utcnow()

        return cls(
            id=uuid4(),
            project_id=project_id,
            issue_number=issue_number,
            title=title,
            description=description,
            type=type,
            status=status,
            priority=priority,
            reporter_id=reporter_id,
            assignee_id=assignee_id,
            due_date=due_date,
            story_points=story_points,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

    def generate_key(self, project_key: str) -> str:
        """Generate issue key in format PROJ-123.

        Args:
            project_key: Project key (e.g., "PROJ")

        Returns:
            Issue key (e.g., "PROJ-123")
        """
        return f"{project_key}-{self.issue_number}"

    def update_title(self, title: str) -> None:
        """Update issue title.

        Args:
            title: New issue title

        Raises:
            ValueError: If title is invalid
        """
        if not title or not title.strip():
            raise ValueError("Issue title cannot be empty")

        title = title.strip()

        if len(title) > 255:
            raise ValueError("Issue title cannot exceed 255 characters")

        self.title = title
        self._touch()

    def update_description(self, description: str | None) -> None:
        """Update issue description.

        Args:
            description: New issue description (can be None)
        """
        self.description = description
        self._touch()

    def update_status(self, status: str) -> None:
        """Update issue status.

        Args:
            status: New issue status

        Raises:
            ValueError: If status is invalid
        """
        valid_statuses = {"todo", "in_progress", "done", "cancelled"}
        if status not in valid_statuses:
            raise ValueError(f"Issue status must be one of: {', '.join(valid_statuses)}")

        self.status = status
        self._touch()

    def update_priority(self, priority: str) -> None:
        """Update issue priority.

        Args:
            priority: New issue priority

        Raises:
            ValueError: If priority is invalid
        """
        valid_priorities = {"low", "medium", "high", "critical"}
        if priority not in valid_priorities:
            raise ValueError(f"Issue priority must be one of: {', '.join(valid_priorities)}")

        self.priority = priority
        self._touch()

    def update_assignee(self, assignee_id: UUID | None) -> None:
        """Update issue assignee.

        Args:
            assignee_id: New assignee user ID (can be None to unassign)
        """
        self.assignee_id = assignee_id
        self._touch()

    def update_due_date(self, due_date: date | None) -> None:
        """Update issue due date.

        Args:
            due_date: New due date (can be None)
        """
        self.due_date = due_date
        self._touch()

    def update_story_points(self, story_points: int | None) -> None:
        """Update issue story points.

        Args:
            story_points: New story points (can be None)

        Raises:
            ValueError: If story points is negative
        """
        if story_points is not None and story_points < 0:
            raise ValueError("Story points cannot be negative")

        self.story_points = story_points
        self._touch()

    def delete(self) -> None:
        """Soft delete issue by setting deleted_at timestamp."""
        self.deleted_at = datetime.utcnow()
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
