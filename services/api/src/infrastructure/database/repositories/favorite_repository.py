"""SQLAlchemy implementation of FavoriteRepository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Favorite
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import FavoriteRepository
from src.domain.value_objects.entity_type import EntityType
from src.infrastructure.database.models import FavoriteModel


class SQLAlchemyFavoriteRepository(FavoriteRepository):
    """SQLAlchemy implementation of FavoriteRepository.

    Adapts the domain FavoriteRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, favorite: Favorite) -> Favorite:
        """Create a new favorite in the database.

        Args:
            favorite: Favorite domain entity

        Returns:
            Created favorite with persisted data

        Raises:
            ConflictException: If favorite already exists (user + entity_type + entity_id)
        """
        # Check if favorite already exists
        if await self.exists(favorite.user_id, favorite.entity_type, favorite.entity_id):
            raise ConflictException(
                f"Favorite already exists for this {favorite.entity_type.value}",
                field="entity_id",
            )

        # Create model from entity
        model = FavoriteModel(
            id=favorite.id,
            user_id=favorite.user_id,
            entity_type=favorite.entity_type.value,
            entity_id=favorite.entity_id,
            created_at=favorite.created_at,
            updated_at=favorite.updated_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, favorite_id: UUID) -> Favorite | None:
        """Get favorite by ID.

        Args:
            favorite_id: Favorite UUID

        Returns:
            Favorite if found, None otherwise
        """
        result = await self._session.execute(
            select(FavoriteModel).where(FavoriteModel.id == favorite_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def delete(self, favorite_id: UUID) -> None:
        """Delete a favorite.

        Args:
            favorite_id: Favorite UUID

        Raises:
            EntityNotFoundException: If favorite not found
        """
        result = await self._session.execute(
            select(FavoriteModel).where(FavoriteModel.id == favorite_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Favorite", str(favorite_id))

        await self._session.delete(model)
        await self._session.flush()

    async def get_all(
        self,
        user_id: UUID,
        entity_type: EntityType | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Favorite]:
        """Get all favorites for a user with optional filtering.

        Args:
            user_id: User UUID
            entity_type: Optional entity type to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of favorites
        """
        query = select(FavoriteModel).where(FavoriteModel.user_id == user_id)

        if entity_type:
            query = query.where(FavoriteModel.entity_type == entity_type.value)

        query = query.offset(skip).limit(limit).order_by(FavoriteModel.created_at.desc())

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count(
        self,
        user_id: UUID,
        entity_type: EntityType | None = None,
    ) -> int:
        """Count total favorites for a user.

        Args:
            user_id: User UUID
            entity_type: Optional entity type to filter by

        Returns:
            Total count of favorites
        """
        query = (
            select(func.count()).select_from(FavoriteModel).where(FavoriteModel.user_id == user_id)
        )

        if entity_type:
            query = query.where(FavoriteModel.entity_type == entity_type.value)

        result = await self._session.execute(query)
        count: int = result.scalar_one()
        return count

    async def exists(
        self,
        user_id: UUID,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> bool:
        """Check if favorite exists.

        Args:
            user_id: User UUID
            entity_type: Entity type
            entity_id: Entity ID

        Returns:
            True if favorite exists, False otherwise
        """
        result = await self._session.execute(
            select(FavoriteModel).where(
                FavoriteModel.user_id == user_id,
                FavoriteModel.entity_type == entity_type.value,
                FavoriteModel.entity_id == entity_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_by_entity(
        self,
        user_id: UUID,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> Favorite | None:
        """Get favorite by user, entity type, and entity ID.

        Args:
            user_id: User UUID
            entity_type: Entity type
            entity_id: Entity ID

        Returns:
            Favorite if found, None otherwise
        """
        result = await self._session.execute(
            select(FavoriteModel).where(
                FavoriteModel.user_id == user_id,
                FavoriteModel.entity_type == entity_type.value,
                FavoriteModel.entity_id == entity_id,
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    def _to_entity(self, model: FavoriteModel) -> Favorite:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: SQLAlchemy FavoriteModel

        Returns:
            Favorite domain entity
        """
        entity_type = EntityType.from_string(model.entity_type)

        return Favorite(
            id=model.id,
            user_id=model.user_id,
            entity_type=entity_type,
            entity_id=model.entity_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
