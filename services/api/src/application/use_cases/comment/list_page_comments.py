"""List page comments use case."""

import math
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.comment import CommentListItemResponse, CommentListResponse
from src.application.dtos.user import UserDTO
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import CommentRepository, PageRepository
from src.infrastructure.database.models import UserModel

logger = structlog.get_logger()


class ListPageCommentsUseCase:
    """Use case for listing comments for a page."""

    def __init__(
        self,
        comment_repository: CommentRepository,
        page_repository: PageRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            comment_repository: Comment repository
            page_repository: Page repository to verify page exists
            session: Database session for loading user details
        """
        self._comment_repository = comment_repository
        self._page_repository = page_repository
        self._session = session

    async def execute(self, page_id: str, page: int = 1, limit: int = 50) -> CommentListResponse:
        """Execute list comments for page.

        Args:
            page_id: Page ID
            page: Page number (1-based)
            limit: Number of items per page

        Returns:
            List of comments response DTO

        Raises:
            EntityNotFoundException: If page not found
        """
        logger.info("Listing comments for page", page_id=page_id, page=page, limit=limit)

        # Verify page exists
        page_uuid = UUID(page_id)
        page_entity = await self._page_repository.get_by_id(page_uuid)
        if page_entity is None:
            logger.warning("Page not found", page_id=page_id)
            raise EntityNotFoundException("Page", page_id)

        # Calculate pagination
        skip = (page - 1) * limit

        # Get comments
        comments = await self._comment_repository.get_by_page_id(page_uuid, skip=skip, limit=limit)
        total = await self._comment_repository.count_by_page_id(page_uuid)

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
                        page_id=comment.page_id,
                        user_id=comment.user_id,
                        user=UserDTO(
                            id=user.id,
                            name=user.name,
                            avatar_url=user.avatar_url,
                        ),
                        content=comment.content,
                        is_edited=comment.is_edited,
                        created_at=comment.created_at,
                        updated_at=comment.updated_at,
                    )
                )

        total_pages = math.ceil(total / limit) if total > 0 else 0

        logger.info(
            "Page comments listed successfully",
            page_id=page_id,
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
