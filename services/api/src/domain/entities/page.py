"""Page domain entity."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4


def generate_page_slug(title: str) -> str:
    """Generate a URL-friendly slug from page title.

    Args:
        title: Page title

    Returns:
        URL-friendly slug (lowercase, hyphens, alphanumeric only)
    """
    # Convert to lowercase
    slug = title.lower()
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
        slug = "page"
    # Limit length to 255 characters (database constraint)
    if len(slug) > 255:
        slug = slug[:255].rstrip("-")
    return slug


@dataclass
class Page:
    """Page domain entity.

    Represents a documentation page in the system.
    Pages are documentation entries within a space.
    Supports hierarchical structure via parent_id.
    This is an aggregate root in DDD terms.
    """

    id: UUID
    space_id: UUID
    title: str
    slug: str
    content: str | None = None
    parent_id: UUID | None = None
    created_by: UUID | None = None
    updated_by: UUID | None = None
    position: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate page entity."""
        if not self.title or not self.title.strip():
            raise ValueError("Page title cannot be empty")

        self.title = self.title.strip()

        if len(self.title) > 255:
            raise ValueError("Page title cannot exceed 255 characters")

        if not self.slug or not self.slug.strip():
            raise ValueError("Page slug cannot be empty")

        self.slug = self.slug.strip().lower()

        if len(self.slug) > 255:
            raise ValueError("Page slug cannot exceed 255 characters")

        # Validate slug format
        if not re.match(r"^[a-z0-9-]+$", self.slug):
            raise ValueError("Page slug must contain only lowercase letters, numbers, and hyphens")

        if self.position < 0:
            raise ValueError("Page position cannot be negative")

    @classmethod
    def create(
        cls,
        space_id: UUID,
        title: str,
        content: str | None = None,
        parent_id: UUID | None = None,
        created_by: UUID | None = None,
        slug: str | None = None,
        position: int = 0,
    ) -> Self:
        """Create a new page.

        Factory method for creating new pages with proper defaults.

        Args:
            space_id: ID of the space this page belongs to
            title: Page title
            content: Optional page content (rich text)
            parent_id: Optional parent page ID for hierarchy
            created_by: ID of the user creating the page
            slug: Optional slug (auto-generated from title if not provided)
            position: Position in the tree (default 0)

        Returns:
            New Page instance

        Raises:
            ValueError: If title is invalid
        """
        now = datetime.utcnow()

        # Auto-generate slug if not provided
        if slug is None:
            slug = generate_page_slug(title)

        return cls(
            id=uuid4(),
            space_id=space_id,
            title=title,
            slug=slug,
            content=content,
            parent_id=parent_id,
            created_by=created_by,
            updated_by=created_by,
            position=position,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

    def update_title(self, title: str, regenerate_slug: bool = False) -> None:
        """Update page title.

        Args:
            title: New page title
            regenerate_slug: If True, regenerate slug from new title

        Raises:
            ValueError: If title is invalid
        """
        if not title or not title.strip():
            raise ValueError("Page title cannot be empty")

        title = title.strip()

        if len(title) > 255:
            raise ValueError("Page title cannot exceed 255 characters")

        self.title = title

        if regenerate_slug:
            self.slug = generate_page_slug(title)

        self._touch()

    def update_slug(self, slug: str) -> None:
        """Update page slug.

        Args:
            slug: New page slug

        Raises:
            ValueError: If slug is invalid
        """
        if not slug or not slug.strip():
            raise ValueError("Page slug cannot be empty")

        slug = slug.strip().lower()

        if len(slug) > 255:
            raise ValueError("Page slug cannot exceed 255 characters")

        # Validate slug format
        if not re.match(r"^[a-z0-9-]+$", slug):
            raise ValueError("Page slug must contain only lowercase letters, numbers, and hyphens")

        self.slug = slug
        self._touch()

    def update_content(self, content: str | None, updated_by: UUID | None = None) -> None:
        """Update page content.

        Args:
            content: New page content (can be None)
            updated_by: ID of the user updating the page
        """
        self.content = content
        if updated_by:
            self.updated_by = updated_by
        self._touch()

    def update_parent(self, parent_id: UUID | None, updated_by: UUID | None = None) -> None:
        """Update page parent (move in hierarchy).

        Args:
            parent_id: New parent page ID (can be None for root level)
            updated_by: ID of the user updating the page
        """
        # Prevent circular reference (parent cannot be self)
        if parent_id == self.id:
            raise ValueError("Page cannot be its own parent")

        self.parent_id = parent_id
        if updated_by:
            self.updated_by = updated_by
        self._touch()

    def update_position(self, position: int, updated_by: UUID | None = None) -> None:
        """Update page position in tree.

        Args:
            position: New position
            updated_by: ID of the user updating the page

        Raises:
            ValueError: If position is negative
        """
        if position < 0:
            raise ValueError("Page position cannot be negative")

        self.position = position
        if updated_by:
            self.updated_by = updated_by
        self._touch()

    def delete(self) -> None:
        """Soft delete page by setting deleted_at timestamp."""
        self.deleted_at = datetime.utcnow()
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
