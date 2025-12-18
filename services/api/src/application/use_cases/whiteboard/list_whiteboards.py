"""List whiteboards use case."""

from math import ceil
from uuid import UUID

import structlog

from src.application.dtos.whiteboard import (
    WhiteboardListItemResponse,
    WhiteboardListResponse,
)
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import SpaceRepository, WhiteboardRepository

logger = structlog.get_logger()


class ListWhiteboardsUseCase:
    """Use case for listing whiteboards with pagination."""

    def __init__(
        self,
        whiteboard_repository: WhiteboardRepository,
        space_repository: SpaceRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            whiteboard_repository: Whiteboard repository
            space_repository: Space repository
        """
        self._whiteboard_repository = whiteboard_repository
        self._space_repository = space_repository

    async def execute(
        self,
        space_id: str,
        page: int = 1,
        limit: int = 20,
    ) -> WhiteboardListResponse:
        """Execute list whiteboards.

        Args:
            space_id: Space ID
            page: Page number (1-based)
            limit: Number of whiteboards per page

        Returns:
            Whiteboard list response DTO with pagination metadata

        Raises:
            EntityNotFoundException: If space not found
        """
        logger.info("Listing whiteboards", space_id=space_id, page=page, limit=limit)

        space_uuid = UUID(space_id)
        # Verify space exists
        space = await self._space_repository.get_by_id(space_uuid)
        if space is None:
            logger.warning("Space not found for listing whiteboards", space_id=space_id)
            raise EntityNotFoundException("Space", space_id)

        offset = (page - 1) * limit

        whiteboards = await self._whiteboard_repository.get_all(
            space_id=space_uuid,
            skip=offset,
            limit=limit,
        )
        total = await self._whiteboard_repository.count(space_id=space_uuid)

        # Calculate total pages
        pages_count = ceil(total / limit) if total > 0 else 0

        whiteboard_responses = [
            WhiteboardListItemResponse(
                id=wb.id,
                space_id=wb.space_id,
                name=wb.name,
                created_by=wb.created_by,
                updated_by=wb.updated_by,
                created_at=wb.created_at,
                updated_at=wb.updated_at,
            )
            for wb in whiteboards
        ]

        logger.info("Whiteboards listed", space_id=space_id, total=total)

        return WhiteboardListResponse(
            whiteboards=whiteboard_responses,
            total=total,
            page=page,
            limit=limit,
            pages_count=pages_count,
        )
