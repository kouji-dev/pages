"""List favorites use case."""

from uuid import UUID

import structlog

from src.application.dtos.favorite import FavoriteListResponse, FavoriteListItemResponse
from src.domain.repositories import FavoriteRepository
from src.domain.value_objects.entity_type import EntityType

logger = structlog.get_logger()


class ListFavoritesUseCase:
    """Use case for listing favorites for a user."""

    def __init__(self, favorite_repository: FavoriteRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            favorite_repository: Favorite repository
        """
        self._favorite_repository = favorite_repository

    async def execute(
        self,
        user_id: str,
        entity_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> FavoriteListResponse:
        """Execute list favorites.

        Args:
            user_id: User UUID
            entity_type: Optional entity type to filter by (project, space, page)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Favorite list response DTO
        """
        user_uuid = UUID(user_id)
        entity_type_vo = EntityType.from_string(entity_type) if entity_type else None

        logger.info(
            "Listing favorites",
            user_id=user_id,
            entity_type=entity_type,
            skip=skip,
            limit=limit,
        )

        favorites = await self._favorite_repository.get_all(
            user_id=user_uuid,
            entity_type=entity_type_vo,
            skip=skip,
            limit=limit,
        )

        total = await self._favorite_repository.count(
            user_id=user_uuid,
            entity_type=entity_type_vo,
        )

        favorite_responses = [
            FavoriteListItemResponse(
                id=favorite.id,
                user_id=favorite.user_id,
                entity_type=favorite.entity_type.value,
                entity_id=favorite.entity_id,
                created_at=favorite.created_at,
                updated_at=favorite.updated_at,
            )
            for favorite in favorites
        ]

        logger.info("Favorites listed", count=len(favorite_responses), total=total)

        return FavoriteListResponse(favorites=favorite_responses, total=total)

