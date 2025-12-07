"""Delete comment use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import CommentRepository, ProjectRepository

logger = structlog.get_logger()


class DeleteCommentUseCase:
    """Use case for deleting a comment (soft delete)."""

    def __init__(
        self,
        comment_repository: CommentRepository,
        project_repository: ProjectRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            comment_repository: Comment repository for data access
            project_repository: Project repository for permission check (for issue comments)
        """
        self._comment_repository = comment_repository
        self._project_repository = project_repository

    async def execute(
        self,
        comment_id: str,
        user_id: UUID,
        is_project_admin: bool = False,
        is_space_admin: bool = False,
    ) -> None:
        """Execute delete comment.

        Args:
            comment_id: Comment ID
            user_id: ID of the user deleting the comment
            is_project_admin: Whether the user is a project admin (for issue comments)
            is_space_admin: Whether the user is a space admin (for page comments)

        Raises:
            EntityNotFoundException: If comment not found
            ValidationException: If user is not authorized to delete
        """
        logger.info("Deleting comment", comment_id=comment_id)

        comment_uuid = UUID(comment_id)
        comment = await self._comment_repository.get_by_id(comment_uuid)

        if comment is None:
            logger.warning("Comment not found for deletion", comment_id=comment_id)
            raise EntityNotFoundException("Comment", comment_id)

        # Check permission: comment author or admin (project admin for issues, space admin for pages)
        is_admin = is_project_admin if comment.entity_type == "issue" else is_space_admin
        if comment.user_id != user_id and not is_admin:
            logger.warning(
                "User not authorized to delete comment",
                comment_id=comment_id,
                user_id=str(user_id),
                comment_author_id=str(comment.user_id),
            )
            admin_type = "project admin" if comment.entity_type == "issue" else "space admin"
            raise ValidationException(
                f"Only the comment author or {admin_type} can delete the comment",
                field="user_id",
            )

        comment.delete()  # Soft delete
        await self._comment_repository.update(comment)

        logger.info("Comment soft-deleted", comment_id=comment_id)
