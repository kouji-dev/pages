"""Delete space use case."""

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import SpaceRepository

logger = structlog.get_logger()


class DeleteSpaceUseCase:
    """Use case for deleting a space."""

    def __init__(self, space_repository: SpaceRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            space_repository: Space repository
        """
        self._space_repository = space_repository

    async def execute(self, space_id: str) -> None:
        """Execute delete space (soft delete).

        Args:
            space_id: Space ID

        Raises:
            EntityNotFoundException: If space not found
        """
        from uuid import UUID

        logger.info("Deleting space", space_id=space_id)

        space_uuid = UUID(space_id)
        space = await self._space_repository.get_by_id(space_uuid)

        if space is None:
            logger.warning("Space not found for deletion", space_id=space_id)
            raise EntityNotFoundException("Space", space_id)

        # Soft delete
        space.delete()
        await self._space_repository.update(space)

        logger.info("Space deleted", space_id=space_id)
