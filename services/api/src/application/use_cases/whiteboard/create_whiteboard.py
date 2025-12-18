"""Create whiteboard use case."""

import structlog

from src.application.dtos.whiteboard import CreateWhiteboardRequest, WhiteboardResponse
from src.domain.entities import Whiteboard
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import SpaceRepository, WhiteboardRepository

logger = structlog.get_logger()


class CreateWhiteboardUseCase:
    """Use case for creating a whiteboard."""

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
        self, request: CreateWhiteboardRequest, created_by: str
    ) -> WhiteboardResponse:
        """Execute create whiteboard.

        Args:
            request: Create whiteboard request
            created_by: ID of the user creating the whiteboard

        Returns:
            Created whiteboard response DTO

        Raises:
            EntityNotFoundException: If space not found
        """
        from uuid import UUID

        logger.info("Creating whiteboard", space_id=str(request.space_id), name=request.name)

        # Verify space exists
        space = await self._space_repository.get_by_id(request.space_id)
        if space is None:
            logger.warning(
                "Space not found for whiteboard creation", space_id=str(request.space_id)
            )
            raise EntityNotFoundException("Space", str(request.space_id))

        # Convert created_by to UUID if provided
        created_by_uuid = UUID(created_by) if created_by else None

        # Ensure data is a string (validator should have converted dict to JSON string)
        data_str: str | None = request.data if isinstance(request.data, str) else None

        # Create whiteboard entity
        whiteboard = Whiteboard.create(
            space_id=request.space_id,
            name=request.name,
            data=data_str,
            created_by=created_by_uuid,
        )

        # Persist whiteboard
        created_whiteboard = await self._whiteboard_repository.create(whiteboard)

        logger.info("Whiteboard created", whiteboard_id=str(created_whiteboard.id))

        return WhiteboardResponse(
            id=created_whiteboard.id,
            space_id=created_whiteboard.space_id,
            name=created_whiteboard.name,
            data=created_whiteboard.data,
            created_by=created_whiteboard.created_by,
            updated_by=created_whiteboard.updated_by,
            created_at=created_whiteboard.created_at,
            updated_at=created_whiteboard.updated_at,
        )
