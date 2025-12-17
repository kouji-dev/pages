"""Delete favorite use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import FavoriteRepository

logger = structlog.get_logger()


class DeleteFavoriteUseCase:
    """Use case for deleting a favorite."""

    def __init__(self, favorite_repository: FavoriteRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            favorite_repository: Favorite repository
        """
        self._favorite_repository = favorite_repository

    async def execute(self, favorite_id: str) -> None:
        """Execute favorite deletion.

        Args:
            favorite_id: Favorite UUID

        Raises:
            EntityNotFoundException: If favorite not found
        """
        logger.info("Deleting favorite", favorite_id=favorite_id)

        favorite_uuid = UUID(favorite_id)
        favorite = await self._favorite_repository.get_by_id(favorite_uuid)

        if favorite is None:
            logger.warning("Favorite not found for deletion", favorite_id=favorite_id)
            raise EntityNotFoundException("Favorite", favorite_id)

        await self._favorite_repository.delete(favorite_uuid)

        logger.info("Favorite deleted successfully", favorite_id=favorite_id)

