"""Create comment use case."""

import json
from uuid import UUID, uuid4

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.comment import CommentResponse, CreateCommentRequest
from src.application.utils.mentions import parse_mentions
from src.domain.entities import Comment
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import CommentRepository, IssueRepository, UserRepository
from src.infrastructure.database.models import NotificationModel, UserModel

logger = structlog.get_logger()


class CreateCommentUseCase:
    """Use case for creating a comment on an issue."""

    def __init__(
        self,
        comment_repository: CommentRepository,
        issue_repository: IssueRepository,
        user_repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            comment_repository: Comment repository
            issue_repository: Issue repository to verify issue exists
            user_repository: User repository to verify user exists
            session: Database session for loading user details
        """
        self._comment_repository = comment_repository
        self._issue_repository = issue_repository
        self._user_repository = user_repository
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

        # Parse @mentions and create notifications
        mentioned_usernames = parse_mentions(request.content)
        if mentioned_usernames:
            # Get mentioned users by email (assuming username is email prefix or email)
            # For now, we'll search by email prefix (before @)
            mentioned_users = []
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
                    mentioned_users.append(mentioned_user_model)

            # Create notification records for mentioned users
            for mentioned_user_model in mentioned_users:
                notification = NotificationModel(
                    id=uuid4(),
                    user_id=mentioned_user_model.id,
                    type="comment_mentioned",
                    title="You were mentioned in a comment",
                    content=f"{author_user_model.name} mentioned you in a comment on issue {issue.title}",
                    entity_type="comment",
                    entity_id=created_comment.id,
                    read=False,
                    data=json.dumps(
                        {
                            "issue_id": str(issue.id),
                            "issue_title": issue.title,
                            "comment_author_id": str(user_uuid),
                            "comment_author_name": author_user_model.name,
                        }
                    ),
                )
                self._session.add(notification)

            if mentioned_users:
                await self._session.flush()
                logger.info(
                    "Created mention notifications",
                    comment_id=str(created_comment.id),
                    mentioned_count=len(mentioned_users),
                )

        # TODO: Create notifications for issue watchers (deferred to 1.6.1)
        # For now, we'll just create notification records without sending

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
