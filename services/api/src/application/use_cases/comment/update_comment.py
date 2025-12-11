"""Update comment use case."""

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.comment import CommentResponse, UpdateCommentRequest
from src.application.dtos.user import UserDTO
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import CommentRepository
from src.infrastructure.database.models import UserModel

logger = structlog.get_logger()


class UpdateCommentUseCase:
    """Use case for updating a comment."""

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

    async def execute(
        self, comment_id: str, request: UpdateCommentRequest, user_id: UUID | None = None
    ) -> CommentResponse:
        """Execute update comment.

        Args:
            comment_id: Comment ID
            request: Comment update request
            user_id: ID of the user updating the comment (for permission check)

        Returns:
            Updated comment response DTO

        Raises:
            EntityNotFoundException: If comment not found
            ValidationException: If comment data is invalid
        """
        logger.info("Updating comment", comment_id=comment_id)

        comment_uuid = UUID(comment_id)
        comment = await self._comment_repository.get_by_id(comment_uuid)

        if comment is None:
            logger.warning("Comment not found for update", comment_id=comment_id)
            raise EntityNotFoundException("Comment", comment_id)

        # Check permission: only comment author can update
        if user_id and comment.user_id != user_id:
            logger.warning(
                "User not authorized to update comment",
                comment_id=comment_id,
                user_id=str(user_id),
                comment_author_id=str(comment.user_id),
            )
            raise ValidationException(
                "Only the comment author can update the comment", field="user_id"
            )

        # Update content
        try:
            comment.update_content(request.content)
        except ValueError as e:
            raise ValidationException(str(e), field="content") from e

        # Save to database
        updated_comment = await self._comment_repository.update(comment)

        # Load user details
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == updated_comment.user_id)
        )
        user_model = result.scalar_one()

        logger.info("Comment updated", comment_id=comment_id)

        # Convert to response DTO
        return CommentResponse(
            id=updated_comment.id,
            entity_type=updated_comment.entity_type,
            entity_id=updated_comment.entity_id,
            issue_id=updated_comment.issue_id,
            user_id=updated_comment.user_id,
            user=UserDTO(
                id=user_model.id,
                name=user_model.name,
                avatar_url=user_model.avatar_url,
            ),
            content=updated_comment.content,
            is_edited=updated_comment.is_edited,
            created_at=updated_comment.created_at,
            updated_at=updated_comment.updated_at,
        )
