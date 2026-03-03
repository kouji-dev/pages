"""Label domain entity."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4


def validate_hex_color(color: str) -> str:
    """Validate and normalize hex color.

    Args:
        color: Hex color string (#RGB or #RRGGBB)

    Returns:
        Normalized hex color (lowercase, with #)

    Raises:
        ValueError: If color format is invalid
    """
    if not color or not color.strip():
        raise ValueError("Color cannot be empty")
    color = color.strip().lower()
    if not color.startswith("#"):
        color = "#" + color
    if not re.match(r"^#[0-9a-f]{3}([0-9a-f]{3})?$", color):
        raise ValueError("Color must be a valid hex code (#RGB or #RRGGBB)")
    return color


@dataclass
class Label:
    """Label domain entity.

    Labels belong to a project and can be attached to issues.
    """

    id: UUID
    project_id: UUID
    name: str
    color: str
    description: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate label entity."""
        if not self.name or not self.name.strip():
            raise ValueError("Label name cannot be empty")
        self.name = self.name.strip()
        if len(self.name) > 100:
            raise ValueError("Label name cannot exceed 100 characters")
        self.color = validate_hex_color(self.color)
        if self.description is not None and len(self.description) > 65535:
            raise ValueError("Label description too long")

    @classmethod
    def create(
        cls,
        project_id: UUID,
        name: str,
        color: str,
        description: str | None = None,
    ) -> Self:
        """Create a new label.

        Args:
            project_id: ID of the project
            name: Label name
            color: Hex color (#RGB or #RRGGBB)
            description: Optional description

        Returns:
            New Label instance
        """
        now = datetime.utcnow()
        color = validate_hex_color(color)
        name = name.strip() if name else ""
        if not name:
            raise ValueError("Label name cannot be empty")
        if len(name) > 100:
            raise ValueError("Label name cannot exceed 100 characters")
        return cls(
            id=uuid4(),
            project_id=project_id,
            name=name,
            color=color,
            description=description,
            created_at=now,
            updated_at=now,
        )

    def update_name(self, name: str) -> None:
        """Update label name."""
        if not name or not name.strip():
            raise ValueError("Label name cannot be empty")
        name = name.strip()
        if len(name) > 100:
            raise ValueError("Label name cannot exceed 100 characters")
        self.name = name
        self._touch()

    def update_color(self, color: str) -> None:
        """Update label color."""
        self.color = validate_hex_color(color)
        self._touch()

    def update_description(self, description: str | None) -> None:
        """Update label description."""
        self.description = description
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
