"""Saved filter domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Self
from uuid import UUID, uuid4


@dataclass
class SavedFilter:
    """Saved filter domain entity.

    Represents a saved search filter that can be reused.
    """

    id: UUID
    user_id: UUID
    project_id: UUID | None
    name: str
    filter_criteria: dict[str, Any]  # JSON structure with filter conditions
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate saved filter."""
        if not self.name or not self.name.strip():
            raise ValueError("Saved filter name cannot be empty")

        self.name = self.name.strip()

        if len(self.name) > 100:
            raise ValueError("Saved filter name cannot exceed 100 characters")

        if not isinstance(self.filter_criteria, dict):
            raise ValueError("Filter criteria must be a dictionary")

    @classmethod
    def create(
        cls,
        user_id: UUID,
        name: str,
        filter_criteria: dict[str, Any],
        project_id: UUID | None = None,
    ) -> Self:
        """Create a new saved filter.

        Args:
            user_id: User ID who owns the filter
            name: Filter name
            filter_criteria: Filter criteria dictionary
            project_id: Optional project ID

        Returns:
            New SavedFilter instance

        Raises:
            ValueError: If filter data is invalid
        """
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            user_id=user_id,
            project_id=project_id,
            name=name,
            filter_criteria=filter_criteria,
            created_at=now,
            updated_at=now,
        )

    def update_name(self, name: str) -> None:
        """Update filter name.

        Args:
            name: New filter name

        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.strip():
            raise ValueError("Saved filter name cannot be empty")

        name = name.strip()

        if len(name) > 100:
            raise ValueError("Saved filter name cannot exceed 100 characters")

        self.name = name
        self._touch()

    def update_criteria(self, filter_criteria: dict[str, Any]) -> None:
        """Update filter criteria.

        Args:
            filter_criteria: New filter criteria

        Raises:
            ValueError: If criteria is invalid
        """
        if not isinstance(filter_criteria, dict):
            raise ValueError("Filter criteria must be a dictionary")

        self.filter_criteria = filter_criteria
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
