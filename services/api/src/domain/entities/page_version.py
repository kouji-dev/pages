"""Page version domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4


@dataclass
class PageVersion:
    """Page version domain entity.

    Represents a historical version of a page.
    This is part of the Page aggregate in DDD terms.
    """

    id: UUID
    page_id: UUID
    version_number: int
    title: str
    content: str | None = None
    created_by: UUID | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate page version entity."""
        if not self.title or not self.title.strip():
            raise ValueError("Page version title cannot be empty")

        self.title = self.title.strip()

        if len(self.title) > 255:
            raise ValueError("Page version title cannot exceed 255 characters")

        if self.version_number < 1:
            raise ValueError("Page version number must be at least 1")

    @classmethod
    def create(
        cls,
        page_id: UUID,
        version_number: int,
        title: str,
        content: str | None = None,
        created_by: UUID | None = None,
    ) -> Self:
        """Create a new page version.

        Factory method for creating new page versions.

        Args:
            page_id: ID of the page this version belongs to
            version_number: Version number (must be >= 1)
            title: Page title at this version
            content: Page content at this version
            created_by: ID of the user creating this version

        Returns:
            New PageVersion instance

        Raises:
            ValueError: If validation fails
        """
        if version_number < 1:
            raise ValueError("Version number must be at least 1")

        return cls(
            id=uuid4(),
            page_id=page_id,
            version_number=version_number,
            title=title.strip(),
            content=content,
            created_by=created_by,
            created_at=datetime.utcnow(),
        )
