"""Comment repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Comment


class CommentRepository(ABC):
    """Abstract comment repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, comment: Comment) -> Comment:
        """Create a new comment.

        Args:
            comment: Comment entity to create

        Returns:
            Created comment with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, comment_id: UUID) -> Comment | None:
        """Get comment by ID.

        Args:
            comment_id: Comment UUID

        Returns:
            Comment if found, None otherwise
        """
        ...

    @abstractmethod
    async def update(self, comment: Comment) -> Comment:
        """Update an existing comment.

        Args:
            comment: Comment entity with updated data

        Returns:
            Updated comment

        Raises:
            EntityNotFoundException: If comment not found
        """
        ...

    @abstractmethod
    async def delete(self, comment_id: UUID) -> None:
        """Hard delete a comment.

        Args:
            comment_id: Comment UUID

        Raises:
            EntityNotFoundException: If comment not found
        """
        ...

    @abstractmethod
    async def get_by_issue_id(
        self,
        issue_id: UUID,
        skip: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> list[Comment]:
        """Get all comments for an issue.

        Args:
            issue_id: Issue UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted comments

        Returns:
            List of comments, ordered by created_at ASC
        """
        ...

    @abstractmethod
    async def count_by_issue_id(
        self, issue_id: UUID, include_deleted: bool = False
    ) -> int:
        """Count total comments for an issue.

        Args:
            issue_id: Issue UUID
            include_deleted: Whether to include soft-deleted comments

        Returns:
            Total count of comments
        """
        ...

