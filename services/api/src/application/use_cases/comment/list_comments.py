"""List comments use case."""

import math
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.comment import CommentListItemResponse, CommentListResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import CommentRepository, IssueRepository
from src.infrastructure.database.models import UserModel

logger = structlog.get_logger()


class ListCommentsUseCase:
    """Use case for listing comments for an issue."""

    def __init__(
        self,
        comment_repository: CommentRepository,
        issue_repository: IssueRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            comment_repository: Comment repository
            issue_repository: Issue repository to verify issue exists
            session: Database session for loading user details
        """
        self._comment_repository = comment_repository
        self._issue_repository = issue_repository
        self._session = session

    async def execute(self, issue_id: str, page: int = 1, limit: int = 50) -> CommentListResponse:
        """Execute list comments for issue.

        Args:
            issue_id: Issue ID
            page: Page number (1-based)
            limit: Number of items per page

        Returns:
            List of comments response DTO

        Raises:
            EntityNotFoundException: If issue not found
        """
        logger.info("Listing comments for issue", issue_id=issue_id, page=page, limit=limit)

        # Verify issue exists
        issue_uuid = UUID(issue_id)
        issue = await self._issue_repository.get_by_id(issue_uuid)
        if issue is None:
            logger.warning("Issue not found", issue_id=issue_id)
            raise EntityNotFoundException("Issue", issue_id)

        # Calculate pagination
        skip = (page - 1) * limit

        # Get comments
        comments = await self._comment_repository.get_by_issue_id(
            issue_uuid, skip=skip, limit=limit
        )
        total = await self._comment_repository.count_by_issue_id(issue_uuid)

        # Load user details for comments
        user_ids = {comment.user_id for comment in comments}
        users_map = {}
        if user_ids:
            result = await self._session.execute(
                select(UserModel).where(UserModel.id.in_(user_ids))
            )
            users = result.scalars().all()
            users_map = {user.id: user for user in users}

        # Convert to response DTOs
        comment_responses = []
        for comment in comments:
            user = users_map.get(comment.user_id)
            if user:
                comment_responses.append(
                    CommentListItemResponse(
                        id=comment.id,
                        entity_type=comment.entity_type,
                        entity_id=comment.entity_id,
                        issue_id=comment.issue_id,
                        user_id=comment.user_id,
                        content=comment.content,
                        is_edited=comment.is_edited,
                        user_name=user.name,
                        user_email=user.email,
                        avatar_url=user.avatar_url,
                        created_at=comment.created_at,
                        updated_at=comment.updated_at,
                    )
                )

        total_pages = math.ceil(total / limit) if total > 0 else 0

        logger.info(
            "Comments listed successfully",
            issue_id=issue_id,
            total=total,
            page=page,
            limit=limit,
        )

        return CommentListResponse(
            comments=comment_responses,
            total=total,
            page=page,
            limit=limit,
            pages=total_pages,
        )
