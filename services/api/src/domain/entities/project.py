"""Project domain entity."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Self
from uuid import UUID, uuid4


def generate_project_key(name: str) -> str:
    """Generate a project key from project name.

    Args:
        name: Project name

    Returns:
        Project key (uppercase, alphanumeric only, max 10 chars)
    """
    # Convert to uppercase
    key = name.upper()
    # Remove all non-alphanumeric characters
    key = re.sub(r"[^A-Z0-9]", "", key)
    # Limit length to 10 characters (database constraint)
    if len(key) > 10:
        key = key[:10]
    # Ensure key is not empty
    if not key:
        key = "PROJ"
    return key


@dataclass
class Project:
    """Project domain entity.

    Represents a project in the system.
    Projects belong to organizations and contain issues.
    This is an aggregate root in DDD terms.
    """

    id: UUID
    organization_id: UUID
    name: str
    key: str
    description: str | None = None
    settings: dict[str, Any] | None = None
    folder_id: UUID | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate project entity."""
        if not self.name or not self.name.strip():
            raise ValueError("Project name cannot be empty")

        self.name = self.name.strip()

        if len(self.name) > 100:
            raise ValueError("Project name cannot exceed 100 characters")

        if not self.key or not self.key.strip():
            raise ValueError("Project key cannot be empty")

        self.key = self.key.strip().upper()

        if len(self.key) > 10:
            raise ValueError("Project key cannot exceed 10 characters")

        # Validate key format (uppercase alphanumeric only)
        if not re.match(r"^[A-Z0-9]+$", self.key):
            raise ValueError("Project key must contain only uppercase letters and numbers")

    @classmethod
    def create(
        cls,
        organization_id: UUID,
        name: str,
        key: str | None = None,
        description: str | None = None,
        settings: dict[str, Any] | None = None,
        folder_id: UUID | None = None,
    ) -> Self:
        """Create a new project.

        Factory method for creating new projects with proper defaults.

        Args:
            organization_id: ID of the organization this project belongs to
            name: Project name
            key: Optional project key (auto-generated from name if not provided)
            description: Optional project description
            settings: Optional project settings dictionary

        Returns:
            New Project instance

        Raises:
            ValueError: If name or key is invalid
        """
        now = datetime.utcnow()

        # Auto-generate key if not provided
        if key is None:
            key = generate_project_key(name)

        return cls(
            id=uuid4(),
            organization_id=organization_id,
            name=name,
            key=key,
            description=description,
            settings=settings,
            folder_id=folder_id,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

    def update_name(self, name: str, regenerate_key: bool = False) -> None:
        """Update project name.

        Args:
            name: New project name
            regenerate_key: If True, regenerate key from new name

        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")

        name = name.strip()

        if len(name) > 100:
            raise ValueError("Project name cannot exceed 100 characters")

        self.name = name

        if regenerate_key:
            self.key = generate_project_key(name)

        self._touch()

    def update_key(self, key: str) -> None:
        """Update project key.

        Args:
            key: New project key

        Raises:
            ValueError: If key is invalid
        """
        if not key or not key.strip():
            raise ValueError("Project key cannot be empty")

        key = key.strip().upper()

        if len(key) > 10:
            raise ValueError("Project key cannot exceed 10 characters")

        # Validate key format
        if not re.match(r"^[A-Z0-9]+$", key):
            raise ValueError("Project key must contain only uppercase letters and numbers")

        self.key = key
        self._touch()

    def update_description(self, description: str | None) -> None:
        """Update project description.

        Args:
            description: New project description (can be None)
        """
        self.description = description
        self._touch()

    def update_settings(self, settings: dict[str, Any] | None) -> None:
        """Update project settings.

        Args:
            settings: New project settings dictionary (can be None)
        """
        self.settings = settings
        self._touch()

    def update_folder(self, folder_id: UUID | None) -> None:
        """Update project folder assignment.

        Args:
            folder_id: New folder ID (None to unassign from folder)
        """
        self.folder_id = folder_id
        self._touch()

    def delete(self) -> None:
        """Soft delete project by setting deleted_at timestamp."""
        self.deleted_at = datetime.utcnow()
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
