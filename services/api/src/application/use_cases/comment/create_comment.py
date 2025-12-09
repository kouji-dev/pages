"""Create comment use case."""

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.comment import CommentResponse, CreateCommentRequest
from src.application.services.notification_service import NotificationService
from src.application.utils.mentions import parse_mentions
from src.domain.entities import Comment
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    CommentRepository,
    IssueRepository,
    NotificationRepository,
    UserRepository,
)
from src.infrastructure.database.models import UserModel

logger = structlog.get_logger()


class CreateCommentUseCase:
    """Use case for creating a comment on an issue."""

    def __init__(
        self,
        comment_repository: CommentRepository,
        issue_repository: IssueRepository,
        user_repository: UserRepository,
        notification_repository: NotificationRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            comment_repository: Comment repository
            issue_repository: Issue repository to verify issue exists
            user_repository: User repository to verify user exists
            notification_repository: Notification repository for creating notifications
            session: Database session for loading user details
        """
        self._comment_repository = comment_repository
        self._issue_repository = issue_repository
        self._user_repository = user_repository
        self._notification_service = NotificationService(notification_repository)
        self._session = session

    async def execute(
        self, issue_id: str, request: CreateCommentRequest, user_id: str
    ) -> CommentResponse:
        """Execute comment creation.

        Args:
            issue_id: Issue ID
            request: Comment creation request
            user_id: ID of the user creating the comment

        Returns:
            Created comment response DTO

        Raises:
            EntityNotFoundException: If issue or user not found
        """
        logger.info(
            "Creating comment",
            issue_id=issue_id,
            user_id=user_id,
        )

        # Verify issue exists
        issue_uuid = UUID(issue_id)
        issue = await self._issue_repository.get_by_id(issue_uuid)
        if issue is None:
            logger.warning("Issue not found for comment creation", issue_id=issue_id)
            raise EntityNotFoundException("Issue", issue_id)

        # Verify user exists
        user_uuid = UUID(user_id)
        user = await self._user_repository.get_by_id(user_uuid)
        if user is None:
            logger.warning("User not found", user_id=user_id)
            raise EntityNotFoundException("User", user_id)

        # Create comment entity
        comment = Comment.create(
            entity_type="issue",
            entity_id=issue_uuid,
            user_id=user_uuid,
            content=request.content,
        )

        # Persist comment
        created_comment = await self._comment_repository.create(comment)

        # Load user model for author details (needed for notifications and response)
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_uuid))
        author_user_model = result.scalar_one()

        # Notify issue reporter/assignee about the comment (if not the commenter)
        comment_preview = created_comment.content[:100] if created_comment.content else ""
        try:
            # Notify issue reporter
            if issue.reporter_id and issue.reporter_id != user_uuid:
                await self._notification_service.notify_issue_commented(
                    user_id=issue.reporter_id,
                    issue_id=issue.id,
                    issue_title=issue.title,
                    commenter_name=author_user_model.name,
                    comment_preview=comment_preview,
                )

            # Notify assignee (if different from reporter and commenter)
            if (
                issue.assignee_id
                and issue.assignee_id != user_uuid
                and issue.assignee_id != issue.reporter_id
            ):
                await self._notification_service.notify_issue_commented(
                    user_id=issue.assignee_id,
                    issue_id=issue.id,
                    issue_title=issue.title,
                    commenter_name=author_user_model.name,
                    comment_preview=comment_preview,
                )

            logger.info(
                "Notification sent for comment",
                comment_id=str(created_comment.id),
                issue_id=str(issue.id),
            )
        except Exception as e:
            # Log error but don't fail the comment creation if notification fails
            logger.warning(
                "Failed to send comment notification",
                error=str(e),
                comment_id=str(created_comment.id),
            )

        # Parse @mentions and create notifications
        mentioned_usernames = parse_mentions(request.content)
        if mentioned_usernames:
            # Get mentioned users by email (assuming username is email prefix or email)
            # For now, we'll search by email prefix (before @)
            for username in mentioned_usernames:
                # Try to find user by email prefix or exact email
                result = await self._session.execute(
                    select(UserModel).where(
                        (UserModel.email.like(f"{username}@%")) | (UserModel.email == username)
                    )
                )
                mentioned_user_model = result.scalar_one_or_none()
                if (
                    mentioned_user_model and mentioned_user_model.id != user_uuid
                ):  # Don't notify the comment author
                    try:
                        await self._notification_service.notify_comment_mentioned(
                            user_id=mentioned_user_model.id,
                            comment_id=created_comment.id,
                            entity_type="issue",
                            entity_id=issue.id,
                            entity_title=issue.title,
                            mentioned_by_name=author_user_model.name,
                        )
                        logger.info(
                            "Mention notification sent",
                            mentioned_user_id=str(mentioned_user_model.id),
                            comment_id=str(created_comment.id),
                        )
                    except Exception as e:
                        # Log error but continue with other mentions
                        logger.warning(
                            "Failed to send mention notification",
                            error=str(e),
                            mentioned_user_id=str(mentioned_user_model.id),
                        )

        # Use author_user_model for response
        user_model = author_user_model

        logger.info(
            "Comment created successfully",
            comment_id=str(created_comment.id),
            issue_id=issue_id,
        )

        # Convert to response DTO
        return CommentResponse(
            id=created_comment.id,
            entity_type=created_comment.entity_type,
            entity_id=created_comment.entity_id,
            issue_id=created_comment.issue_id,
            user_id=created_comment.user_id,
            content=created_comment.content,
            is_edited=created_comment.is_edited,
            user_name=user_model.name,
            user_email=user_model.email,
            avatar_url=user_model.avatar_url,
            created_at=created_comment.created_at,
            updated_at=created_comment.updated_at,
        )
