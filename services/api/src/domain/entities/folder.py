"""Folder domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4


@dataclass
class Folder:
    """Folder domain entity.

    Represents a folder in the system.
    Folders are logical containers for organizing projects and spaces within an organization.
    They support hierarchical structure via parent_id.
    This is an aggregate root in DDD terms.
    """

    id: UUID
    organization_id: UUID
    name: str
    parent_id: UUID | None = None
    position: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate folder entity."""
        if not self.name or not self.name.strip():
            raise ValueError("Folder name cannot be empty")

        self.name = self.name.strip()

        if len(self.name) > 100:
            raise ValueError("Folder name cannot exceed 100 characters")

        if self.position < 0:
            raise ValueError("Folder position cannot be negative")

        # Prevent self-reference
        if self.parent_id == self.id:
            raise ValueError("Folder cannot be its own parent")

    @classmethod
    def create(
        cls,
        organization_id: UUID,
        name: str,
        parent_id: UUID | None = None,
        position: int = 0,
    ) -> Self:
        """Create a new folder.

        Factory method for creating new folders with proper defaults.

        Args:
            organization_id: ID of the organization this folder belongs to
            name: Folder name
            parent_id: Optional parent folder ID for hierarchy
            position: Position/order for display (default: 0)

        Returns:
            New Folder instance

        Raises:
            ValueError: If name is invalid
        """
        now = datetime.utcnow()

        folder = cls(
            id=uuid4(),
            organization_id=organization_id,
            name=name,
            parent_id=parent_id,
            position=position,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        return folder

    def update_name(self, name: str) -> None:
        """Update folder name.

        Args:
            name: New folder name

        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.strip():
            raise ValueError("Folder name cannot be empty")

        name = name.strip()

        if len(name) > 100:
            raise ValueError("Folder name cannot exceed 100 characters")

        self.name = name
        self._touch()

    def update_parent(self, parent_id: UUID | None) -> None:
        """Update folder parent.

        Args:
            parent_id: New parent folder ID (None for root level)

        Raises:
            ValueError: If parent_id is invalid (self-reference)
        """
        # Prevent self-reference
        if parent_id == self.id:
            raise ValueError("Folder cannot be its own parent")

        self.parent_id = parent_id
        self._touch()

    def update_position(self, position: int) -> None:
        """Update folder position.

        Args:
            position: New position/order

        Raises:
            ValueError: If position is negative
        """
        if position < 0:
            raise ValueError("Folder position cannot be negative")

        self.position = position
        self._touch()

    def delete(self) -> None:
        """Soft delete folder by setting deleted_at timestamp."""
        self.deleted_at = datetime.utcnow()
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
