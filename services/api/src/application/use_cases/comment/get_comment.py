"""Get comment use case."""

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.comment import CommentResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import CommentRepository
from src.infrastructure.database.models import UserModel

logger = structlog.get_logger()


class GetCommentUseCase:
    """Use case for retrieving a comment by ID."""

    def __init__(
        self,
        comment_repository: CommentRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            comment_repository: Comment repository
            session: Database session for loading user details
        """
        self._comment_repository = comment_repository
        self._session = session

    async def execute(self, comment_id: str) -> CommentResponse:
        """Execute get comment.

        Args:
            comment_id: Comment ID

        Returns:
            Comment response DTO

        Raises:
            EntityNotFoundException: If comment not found
        """
        logger.info("Getting comment", comment_id=comment_id)

        comment_uuid = UUID(comment_id)
        comment = await self._comment_repository.get_by_id(comment_uuid)

        if comment is None:
            logger.warning("Comment not found", comment_id=comment_id)
            raise EntityNotFoundException("Comment", comment_id)

        # Load user details
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == comment.user_id)
        )
        user_model = result.scalar_one()

        logger.info("Comment retrieved", comment_id=comment_id)

        # Convert to response DTO
        return CommentResponse(
            id=comment.id,
            entity_type=comment.entity_type,
            entity_id=comment.entity_id,
            issue_id=comment.issue_id,
            page_id=comment.page_id,
            user_id=comment.user_id,
            content=comment.content,
            is_edited=comment.is_edited,
            user_name=user_model.name,
            user_email=user_model.email,
            avatar_url=user_model.avatar_url,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )
