"""Update whiteboard use case."""

from uuid import UUID

import structlog

from src.application.dtos.whiteboard import UpdateWhiteboardRequest, WhiteboardResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import WhiteboardRepository

logger = structlog.get_logger()


class UpdateWhiteboardUseCase:
    """Use case for updating a whiteboard."""

    def __init__(self, whiteboard_repository: WhiteboardRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            whiteboard_repository: Whiteboard repository
        """
        self._whiteboard_repository = whiteboard_repository

    async def execute(
        self, whiteboard_id: str, request: UpdateWhiteboardRequest, updated_by: str
    ) -> WhiteboardResponse:
        """Execute update whiteboard.

        Args:
            whiteboard_id: Whiteboard ID
            request: Whiteboard update request
            updated_by: ID of the user updating the whiteboard

        Returns:
            Updated whiteboard response DTO

        Raises:
            EntityNotFoundException: If whiteboard not found
        """
        logger.info("Updating whiteboard", whiteboard_id=whiteboard_id)

        whiteboard_uuid = UUID(whiteboard_id)
        whiteboard = await self._whiteboard_repository.get_by_id(whiteboard_uuid)

        if whiteboard is None:
            logger.warning("Whiteboard not found for update", whiteboard_id=whiteboard_id)
            raise EntityNotFoundException("Whiteboard", whiteboard_id)

        # Convert updated_by to UUID if provided
        updated_by_uuid = UUID(updated_by) if updated_by else None

        # Update fields if provided
        if request.name is not None:
            whiteboard.update_name(request.name, updated_by=updated_by_uuid)

        if request.data is not None:
            whiteboard.update_data(request.data, updated_by=updated_by_uuid)

        # Persist changes
        updated_whiteboard = await self._whiteboard_repository.update(whiteboard)

        logger.info("Whiteboard updated", whiteboard_id=whiteboard_id)

        return WhiteboardResponse(
            id=updated_whiteboard.id,
            space_id=updated_whiteboard.space_id,
            name=updated_whiteboard.name,
            data=updated_whiteboard.data,
            created_by=updated_whiteboard.created_by,
            updated_by=updated_whiteboard.updated_by,
            created_at=updated_whiteboard.created_at,
            updated_at=updated_whiteboard.updated_at,
        )
