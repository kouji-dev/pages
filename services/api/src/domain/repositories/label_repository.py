"""Label repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Label


class LabelRepository(ABC):
    """Abstract label repository interface."""

    @abstractmethod
    async def create(self, label: Label) -> Label:
        """Create a new label.

        Args:
            label: Label entity to create

        Returns:
            Created label with persisted data

        Raises:
            ConflictException: If label name already exists in project
        """
        ...

    @abstractmethod
    async def get_by_id(self, label_id: UUID) -> Label | None:
        """Get label by ID.

        Args:
            label_id: Label UUID

        Returns:
            Label if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_project(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
    ) -> list[Label]:
        """Get labels for a project with optional pagination and search.

        Args:
            project_id: Project UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Optional search by name

        Returns:
            List of labels
        """
        ...

    @abstractmethod
    async def count_by_project(
        self,
        project_id: UUID,
        search: str | None = None,
    ) -> int:
        """Count labels in a project.

        Args:
            project_id: Project UUID
            search: Optional search by name

        Returns:
            Total count
        """
        ...

    @abstractmethod
    async def exists_by_name(
        self, project_id: UUID, name: str, exclude_id: UUID | None = None
    ) -> bool:
        """Check if label with name exists in project.

        Args:
            project_id: Project UUID
            name: Label name
            exclude_id: Optional label ID to exclude

        Returns:
            True if exists, False otherwise
        """
        ...

    @abstractmethod
    async def update(self, label: Label) -> Label:
        """Update an existing label.

        Args:
            label: Label entity with updated data

        Returns:
            Updated label

        Raises:
            EntityNotFoundException: If label not found
            ConflictException: If name conflicts with another label in project
        """
        ...

    @abstractmethod
    async def delete(self, label_id: UUID) -> None:
        """Delete a label (cascade to issue_labels).

        Args:
            label_id: Label UUID

        Raises:
            EntityNotFoundException: If label not found
        """
        ...

    @abstractmethod
    async def add_label_to_issue(self, issue_id: UUID, label_id: UUID) -> None:
        """Add a label to an issue.

        Args:
            issue_id: Issue UUID
            label_id: Label UUID

        Raises:
            EntityNotFoundException: If issue or label not found
            ConflictException: If issue already has this label
        """
        ...

    @abstractmethod
    async def remove_label_from_issue(self, issue_id: UUID, label_id: UUID) -> None:
        """Remove a label from an issue.

        Args:
            issue_id: Issue UUID
            label_id: Label UUID

        Raises:
            EntityNotFoundException: If association not found
        """
        ...

    @abstractmethod
    async def get_labels_for_issue(self, issue_id: UUID) -> list[Label]:
        """Get all labels for an issue.

        Args:
            issue_id: Issue UUID

        Returns:
            List of labels attached to the issue
        """
        ...

    @abstractmethod
    async def issue_has_label(self, issue_id: UUID, label_id: UUID) -> bool:
        """Check if an issue has a specific label.

        Args:
            issue_id: Issue UUID
            label_id: Label UUID

        Returns:
            True if issue has the label, False otherwise
        """
        ...
