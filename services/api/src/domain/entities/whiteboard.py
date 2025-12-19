"""Whiteboard domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4


@dataclass
class Whiteboard:
    """Whiteboard domain entity.

    Represents a collaborative drawing canvas within a space.
    This is an aggregate root in DDD terms.
    """

    id: UUID
    space_id: UUID
    name: str
    data: str | None = None  # JSON data (drawings, shapes, text)
    created_by: UUID | None = None
    updated_by: UUID | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate whiteboard entity."""
        if not self.name or not self.name.strip():
            raise ValueError("Whiteboard name cannot be empty")

        self.name = self.name.strip()

        if len(self.name) > 100:
            raise ValueError("Whiteboard name cannot exceed 100 characters")

    @classmethod
    def create(
        cls,
        space_id: UUID,
        name: str,
        data: str | None = None,
        created_by: UUID | None = None,
    ) -> Self:
        """Create a new whiteboard.

        Factory method for creating new whiteboards.

        Args:
            space_id: ID of the space this whiteboard belongs to
            name: Whiteboard name
            data: Optional whiteboard data (JSON)
            created_by: ID of the user creating the whiteboard

        Returns:
            New Whiteboard instance

        Raises:
            ValueError: If name is invalid
        """
        now = datetime.utcnow()

        return cls(
            id=uuid4(),
            space_id=space_id,
            name=name.strip(),
            data=data,
            created_by=created_by,
            updated_by=created_by,
            created_at=now,
            updated_at=now,
        )

    def update_name(self, name: str, updated_by: UUID | None = None) -> None:
        """Update whiteboard name.

        Args:
            name: New whiteboard name
            updated_by: ID of the user updating the whiteboard

        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.strip():
            raise ValueError("Whiteboard name cannot be empty")

        name = name.strip()

        if len(name) > 100:
            raise ValueError("Whiteboard name cannot exceed 100 characters")

        self.name = name
        if updated_by:
            self.updated_by = updated_by
        self._touch()

    def update_data(self, data: str | None, updated_by: UUID | None = None) -> None:
        """Update whiteboard data.

        Args:
            data: New whiteboard data (JSON)
            updated_by: ID of the user updating the whiteboard
        """
        self.data = data
        if updated_by:
            self.updated_by = updated_by
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
