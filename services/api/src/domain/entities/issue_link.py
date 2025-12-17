"""Issue link domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4


@dataclass
class IssueLink:
    """Issue link domain entity.

    Represents a link between two issues (e.g., Blocks, Blocked by, Relates to).
    """

    id: UUID
    source_issue_id: UUID
    target_issue_id: UUID
    link_type: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    VALID_LINK_TYPES = {
        "blocks",
        "blocked_by",
        "relates_to",
        "duplicate",
        "duplicated_by",
    }

    def __post_init__(self) -> None:
        """Validate issue link."""
        if self.source_issue_id == self.target_issue_id:
            raise ValueError("Issue cannot link to itself")

        if self.link_type not in self.VALID_LINK_TYPES:
            raise ValueError(f"Link type must be one of: {', '.join(self.VALID_LINK_TYPES)}")

    @classmethod
    def create(
        cls,
        source_issue_id: UUID,
        target_issue_id: UUID,
        link_type: str,
    ) -> Self:
        """Create a new issue link.

        Args:
            source_issue_id: Source issue ID
            target_issue_id: Target issue ID
            link_type: Type of link

        Returns:
            New IssueLink instance

        Raises:
            ValueError: If link is invalid
        """
        if source_issue_id == target_issue_id:
            raise ValueError("Issue cannot link to itself")

        if link_type not in cls.VALID_LINK_TYPES:
            raise ValueError(f"Link type must be one of: {', '.join(cls.VALID_LINK_TYPES)}")

        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            source_issue_id=source_issue_id,
            target_issue_id=target_issue_id,
            link_type=link_type,
            created_at=now,
            updated_at=now,
        )

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
