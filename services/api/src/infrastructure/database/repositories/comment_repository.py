"""SQLAlchemy implementation of CommentRepository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Comment
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.comment_repository import CommentRepository
from src.infrastructure.database.models import CommentModel


class SQLAlchemyCommentRepository(CommentRepository):
    """SQLAlchemy implementation of CommentRepository.

    Adapts the domain CommentRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, comment: Comment) -> Comment:
        """Create a new comment in the database.

        Args:
            comment: Comment domain entity

        Returns:
            Created comment with persisted data
        """
        # Create model from entity
        model = CommentModel(
            id=comment.id,
            entity_type=comment.entity_type,
            entity_id=comment.entity_id,
            issue_id=comment.issue_id,
            page_id=comment.page_id,
            user_id=comment.user_id,
            content=comment.content,
            is_edited=comment.is_edited,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            deleted_at=comment.deleted_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, comment_id: UUID) -> Comment | None:
        """Get comment by ID.

        Args:
            comment_id: Comment UUID

        Returns:
            Comment if found, None otherwise
        """
        result = await self._session.execute(
            select(CommentModel).where(CommentModel.id == comment_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def update(self, comment: Comment) -> Comment:
        """Update an existing comment.

        Args:
            comment: Comment entity with updated data

        Returns:
            Updated comment

        Raises:
            EntityNotFoundException: If comment not found
        """
        result = await self._session.execute(
            select(CommentModel).where(CommentModel.id == comment.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Comment", str(comment.id))

        # Update model fields
        model.content = comment.content
        model.is_edited = comment.is_edited
        model.updated_at = comment.updated_at
        model.deleted_at = comment.deleted_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, comment_id: UUID) -> None:
        """Hard delete a comment.

        Args:
            comment_id: Comment UUID

        Raises:
            EntityNotFoundException: If comment not found
        """
        result = await self._session.execute(
            select(CommentModel).where(CommentModel.id == comment_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Comment", str(comment_id))

        await self._session.delete(model)
        await self._session.flush()

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
        query = (
            select(CommentModel)
            .where(CommentModel.issue_id == issue_id)
            .order_by(CommentModel.created_at.asc())
            .offset(skip)
            .limit(limit)
        )

        if not include_deleted:
            query = query.where(CommentModel.deleted_at.is_(None))

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count_by_issue_id(self, issue_id: UUID, include_deleted: bool = False) -> int:
        """Count total comments for an issue.

        Args:
            issue_id: Issue UUID
            include_deleted: Whether to include soft-deleted comments

        Returns:
            Total count of comments
        """
        query = select(func.count(CommentModel.id)).where(CommentModel.issue_id == issue_id)

        if not include_deleted:
            query = query.where(CommentModel.deleted_at.is_(None))

        result = await self._session.execute(query)
        return result.scalar_one() or 0

    def _to_entity(self, model: CommentModel) -> Comment:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: SQLAlchemy CommentModel

        Returns:
            Comment domain entity
        """
        return Comment(
            id=model.id,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            issue_id=model.issue_id,
            page_id=model.page_id,
            user_id=model.user_id,
            content=model.content,
            is_edited=model.is_edited,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
