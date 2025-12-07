"""Create page use case."""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.page import CreatePageRequest, PageResponse
from src.domain.entities import Page
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageRepository, SpaceRepository, UserRepository
from src.infrastructure.database.models import CommentModel

logger = structlog.get_logger()


class CreatePageUseCase:
    """Use case for creating a page."""

    def __init__(
        self,
        page_repository: PageRepository,
        space_repository: SpaceRepository,
        user_repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            page_repository: Page repository
            space_repository: Space repository to verify space exists
            user_repository: User repository to verify creator exists
            session: Database session for counting comments
        """
        self._page_repository = page_repository
        self._space_repository = space_repository
        self._user_repository = user_repository
        self._session = session

    async def execute(self, request: CreatePageRequest, creator_user_id: str) -> PageResponse:
        """Execute page creation.

        Args:
            request: Page creation request
            creator_user_id: ID of the user creating the page

        Returns:
            Created page response DTO with comment count

        Raises:
            EntityNotFoundException: If space, parent page, or creator user not found
        """
        logger.info(
            "Creating page",
            title=request.title,
            space_id=str(request.space_id),
            parent_id=str(request.parent_id) if request.parent_id else None,
            creator_user_id=creator_user_id,
        )

        # Verify space exists
        space = await self._space_repository.get_by_id(request.space_id)
        if space is None:
            logger.warning(
                "Space not found for page creation",
                space_id=str(request.space_id),
            )
            raise EntityNotFoundException("Space", str(request.space_id))

        # Verify parent page exists if provided
        if request.parent_id:
            parent = await self._page_repository.get_by_id(request.parent_id)
            if parent is None:
                logger.warning("Parent page not found", parent_id=str(request.parent_id))
                raise EntityNotFoundException("Page", str(request.parent_id))
            # Verify parent is in the same space
            if parent.space_id != request.space_id:
                raise ValueError("Parent page must be in the same space")

        # Verify creator exists
        creator_uuid = UUID(creator_user_id)
        creator = await self._user_repository.get_by_id(creator_uuid)
        if creator is None:
            logger.warning("Creator user not found", creator_user_id=creator_user_id)
            raise EntityNotFoundException("User", creator_user_id)

        # Create page entity
        page = Page.create(
            space_id=request.space_id,
            title=request.title,
            content=request.content,
            parent_id=request.parent_id,
            created_by=creator_uuid,
            slug=request.slug,
            position=request.position,
        )

        # Persist page
        created_page = await self._page_repository.create(page)

        # Count comments (will be 0 for new page)
        result = await self._session.execute(
            select(func.count())
            .select_from(CommentModel)
            .where(CommentModel.page_id == created_page.id)
        )
        comment_count: int = result.scalar_one()

        logger.info(
            "Page created successfully",
            page_id=str(created_page.id),
            slug=created_page.slug,
        )

        return PageResponse(
            id=created_page.id,
            space_id=created_page.space_id,
            title=created_page.title,
            slug=created_page.slug,
            content=created_page.content,
            parent_id=created_page.parent_id,
            created_by=created_page.created_by,
            updated_by=created_page.updated_by,
            position=created_page.position,
            comment_count=comment_count,
            created_at=created_page.created_at,
            updated_at=created_page.updated_at,
        )
