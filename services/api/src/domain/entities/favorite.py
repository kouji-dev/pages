"""Favorite domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4

from src.domain.value_objects.entity_type import EntityType


@dataclass
class Favorite:
    """Favorite domain entity.

    Represents a favorite item in the system.
    Favorites are heterogeneous - they can reference projects, spaces, or pages.
    This is an aggregate root in DDD terms.
    """

    id: UUID
    user_id: UUID
    entity_type: EntityType
    entity_id: UUID
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate favorite entity."""
        if not self.entity_id:
            raise ValueError("Entity ID cannot be empty")

    @classmethod
    def create(
        cls,
        user_id: UUID,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> Self:
        """Create a new favorite.

        Factory method for creating new favorites with proper defaults.

        Args:
            user_id: ID of the user who favorited the item
            entity_type: Type of entity (project, space, or page)
            entity_id: ID of the favorited entity

        Returns:
            New Favorite instance

        Raises:
            ValueError: If entity_id is invalid
        """
        now = datetime.utcnow()

        favorite = cls(
            id=uuid4(),
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            created_at=now,
            updated_at=now,
        )

        return favorite

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

