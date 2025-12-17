"""Issue link repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.issue_link import IssueLink


class IssueLinkRepository(ABC):
    """Abstract issue link repository interface."""

    @abstractmethod
    async def create(self, link: IssueLink) -> IssueLink:
        """Create a new issue link."""
        ...

    @abstractmethod
    async def get_by_id(self, link_id: UUID) -> IssueLink | None:
        """Get issue link by ID."""
        ...

    @abstractmethod
    async def get_by_issue_id(self, issue_id: UUID) -> list[IssueLink]:
        """Get all links for an issue (both as source and target)."""
        ...

    @abstractmethod
    async def get_outgoing_links(self, issue_id: UUID) -> list[IssueLink]:
        """Get outgoing links from an issue."""
        ...

    @abstractmethod
    async def get_incoming_links(self, issue_id: UUID) -> list[IssueLink]:
        """Get incoming links to an issue."""
        ...

    @abstractmethod
    async def delete(self, link_id: UUID) -> None:
        """Delete an issue link."""
        ...

    @abstractmethod
    async def exists(self, source_issue_id: UUID, target_issue_id: UUID, link_type: str) -> bool:
        """Check if a link exists."""
        ...

    @abstractmethod
    async def check_circular_dependency(self, source_issue_id: UUID, target_issue_id: UUID) -> bool:
        """Check if creating a link would create a circular dependency."""
        ...
