"""Create favorite use case."""

from uuid import UUID

import structlog

from src.application.dtos.favorite import CreateFavoriteRequest, FavoriteResponse
from src.domain.entities import Favorite
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import FavoriteRepository, UserRepository
from src.domain.value_objects.entity_type import EntityType

logger = structlog.get_logger()


class CreateFavoriteUseCase:
    """Use case for creating a favorite."""

    def __init__(
        self,
        favorite_repository: FavoriteRepository,
        user_repository: UserRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            favorite_repository: Favorite repository
            user_repository: User repository to verify user exists
        """
        self._favorite_repository = favorite_repository
        self._user_repository = user_repository

    async def execute(self, request: CreateFavoriteRequest, user_id: str) -> FavoriteResponse:
        """Execute favorite creation.

        Args:
            request: Favorite creation request
            user_id: ID of the user creating the favorite

        Returns:
            Created favorite response DTO

        Raises:
            EntityNotFoundException: If user not found
            ConflictException: If favorite already exists
        """
        logger.info(
            "Creating favorite",
            entity_type=request.entity_type,
            entity_id=str(request.entity_id),
            user_id=user_id,
        )

        # Verify user exists
        user_uuid = UUID(user_id)
        user = await self._user_repository.get_by_id(user_uuid)
        if user is None:
            logger.warning("User not found for favorite creation", user_id=user_id)
            raise EntityNotFoundException("User", user_id)

        # Create EntityType value object
        entity_type = EntityType.from_string(request.entity_type)

        # Check if favorite already exists
        if await self._favorite_repository.exists(user_uuid, entity_type, request.entity_id):
            logger.warning(
                "Favorite already exists",
                user_id=user_id,
                entity_type=request.entity_type,
                entity_id=str(request.entity_id),
            )
            raise ConflictException(
                f"Favorite already exists for this {request.entity_type}",
                field="entity_id",
            )

        # Create favorite entity
        favorite = Favorite.create(
            user_id=user_uuid,
            entity_type=entity_type,
            entity_id=request.entity_id,
        )

        # Persist favorite
        created_favorite = await self._favorite_repository.create(favorite)

        logger.info(
            "Favorite created successfully",
            favorite_id=str(created_favorite.id),
            entity_type=created_favorite.entity_type.value,
        )

        return FavoriteResponse(
            id=created_favorite.id,
            user_id=created_favorite.user_id,
            entity_type=created_favorite.entity_type.value,
            entity_id=created_favorite.entity_id,
            created_at=created_favorite.created_at,
            updated_at=created_favorite.updated_at,
        )
