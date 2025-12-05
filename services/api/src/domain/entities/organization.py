"""Organization domain entity."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Self
from uuid import UUID, uuid4


def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from organization name.

    Args:
        name: Organization name

    Returns:
        URL-friendly slug (lowercase, hyphens, alphanumeric only)
    """
    # Convert to lowercase
    slug = name.lower()
    # Replace spaces and underscores with hyphens
    slug = re.sub(r"[_\s]+", "-", slug)
    # Remove all non-alphanumeric characters except hyphens
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    # Replace multiple hyphens with single hyphen
    slug = re.sub(r"-+", "-", slug)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    # Ensure slug is not empty
    if not slug:
        slug = "organization"
    # Limit length to 100 characters (database constraint)
    if len(slug) > 100:
        slug = slug[:100].rstrip("-")
    return slug


@dataclass
class Organization:
    """Organization domain entity.

    Represents an organization in the system.
    This is an aggregate root in DDD terms.
    """

    id: UUID
    name: str
    slug: str
    description: str | None = None
    settings: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate organization entity."""
        if not self.name or not self.name.strip():
            raise ValueError("Organization name cannot be empty")

        self.name = self.name.strip()

        if len(self.name) > 100:
            raise ValueError("Organization name cannot exceed 100 characters")

        if not self.slug or not self.slug.strip():
            raise ValueError("Organization slug cannot be empty")

        self.slug = self.slug.strip().lower()

        if len(self.slug) > 100:
            raise ValueError("Organization slug cannot exceed 100 characters")

        # Validate slug format
        if not re.match(r"^[a-z0-9-]+$", self.slug):
            raise ValueError(
                "Organization slug must contain only lowercase letters, numbers, and hyphens"
            )

    @classmethod
    def create(
        cls,
        name: str,
        slug: str | None = None,
        description: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> Self:
        """Create a new organization.

        Factory method for creating new organizations with proper defaults.

        Args:
            name: Organization name
            slug: Optional slug (auto-generated from name if not provided)
            description: Optional organization description
            settings: Optional organization settings dictionary

        Returns:
            New Organization instance

        Raises:
            ValueError: If name is invalid
        """
        now = datetime.utcnow()

        # Auto-generate slug if not provided
        if slug is None:
            slug = generate_slug(name)

        return cls(
            id=uuid4(),
            name=name,
            slug=slug,
            description=description,
            settings=settings,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

    def update_name(self, name: str, regenerate_slug: bool = False) -> None:
        """Update organization name.

        Args:
            name: New organization name
            regenerate_slug: If True, regenerate slug from new name

        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.strip():
            raise ValueError("Organization name cannot be empty")

        name = name.strip()

        if len(name) > 100:
            raise ValueError("Organization name cannot exceed 100 characters")

        self.name = name

        if regenerate_slug:
            self.slug = generate_slug(name)

        self._touch()

    def update_slug(self, slug: str) -> None:
        """Update organization slug.

        Args:
            slug: New organization slug

        Raises:
            ValueError: If slug is invalid
        """
        if not slug or not slug.strip():
            raise ValueError("Organization slug cannot be empty")

        slug = slug.strip().lower()

        if len(slug) > 100:
            raise ValueError("Organization slug cannot exceed 100 characters")

        # Validate slug format
        if not re.match(r"^[a-z0-9-]+$", slug):
            raise ValueError(
                "Organization slug must contain only lowercase letters, numbers, and hyphens"
            )

        self.slug = slug
        self._touch()

    def update_description(self, description: str | None) -> None:
        """Update organization description.

        Args:
            description: New organization description (can be None)
        """
        self.description = description
        self._touch()

    def update_settings(self, settings: dict[str, Any] | None) -> None:
        """Update organization settings.

        Args:
            settings: New organization settings dictionary (can be None)
        """
        self.settings = settings
        self._touch()

    def delete(self) -> None:
        """Soft delete organization by setting deleted_at timestamp."""
        self.deleted_at = datetime.utcnow()
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
