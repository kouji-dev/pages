"""Delete whiteboard use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import WhiteboardRepository

logger = structlog.get_logger()


class DeleteWhiteboardUseCase:
    """Use case for deleting a whiteboard."""

    def __init__(self, whiteboard_repository: WhiteboardRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            whiteboard_repository: Whiteboard repository
        """
        self._whiteboard_repository = whiteboard_repository

    async def execute(self, whiteboard_id: str) -> None:
        """Execute delete whiteboard.

        Args:
            whiteboard_id: Whiteboard ID

        Raises:
            EntityNotFoundException: If whiteboard not found
        """
        logger.info("Deleting whiteboard", whiteboard_id=whiteboard_id)

        whiteboard_uuid = UUID(whiteboard_id)
        whiteboard = await self._whiteboard_repository.get_by_id(whiteboard_uuid)

        if whiteboard is None:
            logger.warning("Whiteboard not found for deletion", whiteboard_id=whiteboard_id)
            raise EntityNotFoundException("Whiteboard", whiteboard_id)

        await self._whiteboard_repository.delete(whiteboard_uuid)

        logger.info("Whiteboard deleted", whiteboard_id=whiteboard_id)
