"""Update page use case."""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.page import PageResponse, UpdatePageRequest
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageRepository
from src.infrastructure.database.models import CommentModel

logger = structlog.get_logger()


class UpdatePageUseCase:
    """Use case for updating a page."""

    def __init__(
        self,
        page_repository: PageRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            page_repository: Page repository
            session: Database session for counting comments
        """
        self._page_repository = page_repository
        self._session = session

    async def execute(
        self, page_id: str, request: UpdatePageRequest, updater_user_id: str
    ) -> PageResponse:
        """Execute update page.

        Args:
            page_id: Page ID
            request: Page update request
            updater_user_id: ID of the user updating the page

        Returns:
            Updated page response DTO with comment count

        Raises:
            EntityNotFoundException: If page not found
        """
        logger.info("Updating page", page_id=page_id)

        page_uuid = UUID(page_id)
        updater_uuid = UUID(updater_user_id)
        page = await self._page_repository.get_by_id(page_uuid)

        if page is None:
            logger.warning("Page not found for update", page_id=page_id)
            raise EntityNotFoundException("Page", page_id)

        # Verify parent page exists if provided and changed
        if request.parent_id is not None and request.parent_id != page.parent_id:
            parent = await self._page_repository.get_by_id(request.parent_id)
            if parent is None:
                logger.warning("Parent page not found", parent_id=str(request.parent_id))
                raise EntityNotFoundException("Page", str(request.parent_id))
            # Verify parent is in the same space
            if parent.space_id != page.space_id:
                raise ValueError("Parent page must be in the same space")

        # Update fields if provided
        if request.title is not None:
            page.update_title(request.title, regenerate_slug=False)

        if request.slug is not None:
            page.update_slug(request.slug)

        if request.content is not None:
            page.update_content(request.content, updated_by=updater_uuid)

        if request.parent_id is not None:
            page.update_parent(request.parent_id, updated_by=updater_uuid)

        if request.position is not None:
            page.update_position(request.position, updated_by=updater_uuid)

        # Persist changes
        updated_page = await self._page_repository.update(page)

        # Count comments
        result = await self._session.execute(
            select(func.count()).select_from(CommentModel).where(CommentModel.page_id == page_uuid)
        )
        comment_count: int = result.scalar_one()

        logger.info("Page updated", page_id=page_id)

        return PageResponse(
            id=updated_page.id,
            space_id=updated_page.space_id,
            title=updated_page.title,
            slug=updated_page.slug,
            content=updated_page.content,
            parent_id=updated_page.parent_id,
            created_by=updated_page.created_by,
            updated_by=updated_page.updated_by,
            position=updated_page.position,
            comment_count=comment_count,
            created_at=updated_page.created_at,
            updated_at=updated_page.updated_at,
        )
