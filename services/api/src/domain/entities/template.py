"""Template domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4


@dataclass
class Template:
    """Template domain entity.

    Represents a page template in the system.
    Templates provide pre-defined content structures for creating pages.
    This is an aggregate root in DDD terms.
    """

    id: UUID
    organization_id: UUID
    name: str
    description: str | None = None
    content: str | None = None  # Template content (HTML or Markdown)
    is_default: bool = False  # Whether this is a default template
    created_by: UUID | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate template entity."""
        if not self.name or not self.name.strip():
            raise ValueError("Template name cannot be empty")

        self.name = self.name.strip()

        if len(self.name) > 100:
            raise ValueError("Template name cannot exceed 100 characters")

        if self.description and len(self.description) > 500:
            raise ValueError("Template description cannot exceed 500 characters")

    @classmethod
    def create(
        cls,
        organization_id: UUID,
        name: str,
        content: str | None = None,
        description: str | None = None,
        is_default: bool = False,
        created_by: UUID | None = None,
    ) -> Self:
        """Create a new template.

        Factory method for creating new templates with proper defaults.

        Args:
            organization_id: ID of the organization this template belongs to
            name: Template name
            content: Optional template content
            description: Optional template description
            is_default: Whether this is a default template
            created_by: ID of the user creating the template

        Returns:
            New Template instance

        Raises:
            ValueError: If name is invalid
        """
        now = datetime.utcnow()

        return cls(
            id=uuid4(),
            organization_id=organization_id,
            name=name,
            description=description,
            content=content,
            is_default=is_default,
            created_by=created_by,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

    def update_name(self, name: str) -> None:
        """Update template name.

        Args:
            name: New template name

        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.strip():
            raise ValueError("Template name cannot be empty")

        name = name.strip()

        if len(name) > 100:
            raise ValueError("Template name cannot exceed 100 characters")

        self.name = name
        self._touch()

    def update_description(self, description: str | None) -> None:
        """Update template description.

        Args:
            description: New template description (can be None)
        """
        if description and len(description) > 500:
            raise ValueError("Template description cannot exceed 500 characters")

        self.description = description
        self._touch()

    def update_content(self, content: str | None) -> None:
        """Update template content.

        Args:
            content: New template content (can be None)
        """
        self.content = content
        self._touch()

    def delete(self) -> None:
        """Soft delete template by setting deleted_at timestamp."""
        self.deleted_at = datetime.utcnow()
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
