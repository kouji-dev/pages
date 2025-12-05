"""Comment domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4


@dataclass
class Comment:
    """Comment domain entity.

    Represents a comment on an issue or page.
    """

    id: UUID
    entity_type: str  # 'issue' or 'page'
    entity_id: UUID
    user_id: UUID
    content: str
    issue_id: UUID | None = None  # Direct FK for performance
    page_id: UUID | None = None  # Direct FK for performance
    is_edited: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate comment entity."""
        if not self.content or not self.content.strip():
            raise ValueError("Comment content cannot be empty")

        self.content = self.content.strip()

        if len(self.content) > 10000:
            raise ValueError("Comment content cannot exceed 10000 characters")

        valid_entity_types = {"issue", "page"}
        if self.entity_type not in valid_entity_types:
            raise ValueError(
                f"Entity type must be one of: {', '.join(valid_entity_types)}"
            )

        # Ensure issue_id or page_id matches entity_type
        if self.entity_type == "issue" and self.issue_id != self.entity_id:
            raise ValueError("issue_id must match entity_id for issue comments")
        if self.entity_type == "page" and self.page_id != self.entity_id:
            raise ValueError("page_id must match entity_id for page comments")

    @classmethod
    def create(
        cls,
        entity_type: str,
        entity_id: UUID,
        user_id: UUID,
        content: str,
        issue_id: UUID | None = None,
        page_id: UUID | None = None,
    ) -> Self:
        """Create a new comment.

        Factory method for creating new comments.

        Args:
            entity_type: Type of entity ('issue' or 'page')
            entity_id: ID of the entity being commented on
            user_id: ID of the user creating the comment
            content: Comment content
            issue_id: Optional direct FK to issue (for performance)
            page_id: Optional direct FK to page (for performance)

        Returns:
            New Comment instance

        Raises:
            ValueError: If content or entity_type is invalid
        """
        # Set direct FK based on entity_type
        if entity_type == "issue":
            issue_id = entity_id
            page_id = None
        elif entity_type == "page":
            page_id = entity_id
            issue_id = None
        else:
            raise ValueError(f"Invalid entity_type: {entity_type}")

        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            entity_type=entity_type,
            entity_id=entity_id,
            issue_id=issue_id,
            page_id=page_id,
            user_id=user_id,
            content=content,
            is_edited=False,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

    def update_content(self, content: str) -> None:
        """Update comment content.

        Args:
            content: New comment content

        Raises:
            ValueError: If content is invalid
        """
        if not content or not content.strip():
            raise ValueError("Comment content cannot be empty")

        content = content.strip()

        if len(content) > 10000:
            raise ValueError("Comment content cannot exceed 10000 characters")

        self.content = content
        self.is_edited = True
        self._touch()

    def delete(self) -> None:
        """Soft delete comment by setting deleted_at timestamp."""
        self.deleted_at = datetime.utcnow()
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

