"""Get whiteboard use case."""

from uuid import UUID

import structlog

from src.application.dtos.whiteboard import WhiteboardResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import WhiteboardRepository

logger = structlog.get_logger()


class GetWhiteboardUseCase:
    """Use case for getting a whiteboard by ID."""

    def __init__(self, whiteboard_repository: WhiteboardRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            whiteboard_repository: Whiteboard repository
        """
        self._whiteboard_repository = whiteboard_repository

    async def execute(self, whiteboard_id: str) -> WhiteboardResponse:
        """Execute get whiteboard.

        Args:
            whiteboard_id: Whiteboard ID

        Returns:
            Whiteboard response DTO

        Raises:
            EntityNotFoundException: If whiteboard not found
        """
        logger.info("Getting whiteboard", whiteboard_id=whiteboard_id)

        whiteboard_uuid = UUID(whiteboard_id)
        whiteboard = await self._whiteboard_repository.get_by_id(whiteboard_uuid)

        if whiteboard is None:
            logger.warning("Whiteboard not found", whiteboard_id=whiteboard_id)
            raise EntityNotFoundException("Whiteboard", whiteboard_id)

        logger.info("Whiteboard retrieved", whiteboard_id=whiteboard_id)

        return WhiteboardResponse(
            id=whiteboard.id,
            space_id=whiteboard.space_id,
            name=whiteboard.name,
            data=whiteboard.data,
            created_by=whiteboard.created_by,
            updated_by=whiteboard.updated_by,
            created_at=whiteboard.created_at,
            updated_at=whiteboard.updated_at,
        )
