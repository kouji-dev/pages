"""SQLAlchemy implementation of SpaceRepository."""

import json
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Space
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import SpaceRepository
from src.infrastructure.database.models import SpaceModel


class SQLAlchemySpaceRepository(SpaceRepository):
    """SQLAlchemy implementation of SpaceRepository.

    Adapts the domain SpaceRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, space: Space) -> Space:
        """Create a new space in the database.

        Args:
            space: Space domain entity

        Returns:
            Created space with persisted data

        Raises:
            ConflictException: If space key already exists in organization
        """
        # Check for existing key in organization
        if await self.exists_by_key(space.organization_id, space.key):
            raise ConflictException(
                f"Space with key '{space.key}' already exists in this organization",
                field="key",
            )

        # Create model from entity
        model = SpaceModel(
            id=space.id,
            organization_id=space.organization_id,
            name=space.name,
            key=space.key,
            description=space.description,
            settings=json.dumps(space.settings) if space.settings else None,
            created_at=space.created_at,
            updated_at=space.updated_at,
            deleted_at=space.deleted_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, space_id: UUID) -> Space | None:
        """Get space by ID.

        Args:
            space_id: Space UUID

        Returns:
            Space if found, None otherwise
        """
        result = await self._session.execute(select(SpaceModel).where(SpaceModel.id == space_id))
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_key(self, organization_id: UUID, key: str) -> Space | None:
        """Get space by key within an organization.

        Args:
            organization_id: Organization UUID
            key: Space key

        Returns:
            Space if found, None otherwise
        """
        result = await self._session.execute(
            select(SpaceModel).where(
                SpaceModel.organization_id == organization_id,
                SpaceModel.key == key.upper(),
                SpaceModel.deleted_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def update(self, space: Space) -> Space:
        """Update an existing space.

        Args:
            space: Space entity with updated data

        Returns:
            Updated space

        Raises:
            EntityNotFoundException: If space not found
            ConflictException: If key conflicts with another space in the organization
        """
        result = await self._session.execute(select(SpaceModel).where(SpaceModel.id == space.id))
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Space", str(space.id))

        # Check for key conflict if key changed
        if model.key != space.key:
            if await self.exists_by_key(space.organization_id, space.key, exclude_id=space.id):
                raise ConflictException(
                    f"Space with key '{space.key}' already exists in this organization",
                    field="key",
                )

        # Update model fields
        model.organization_id = space.organization_id
        model.name = space.name
        model.key = space.key
        model.description = space.description
        model.settings = json.dumps(space.settings) if space.settings else None
        model.updated_at = space.updated_at
        model.deleted_at = space.deleted_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, space_id: UUID) -> None:
        """Hard delete a space.

        Args:
            space_id: Space UUID

        Raises:
            EntityNotFoundException: If space not found
        """
        result = await self._session.execute(select(SpaceModel).where(SpaceModel.id == space_id))
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Space", str(space_id))

        await self._session.delete(model)
        await self._session.flush()

    async def exists_by_key(
        self, organization_id: UUID, key: str, exclude_id: UUID | None = None
    ) -> bool:
        """Check if space with key exists in organization.

        Args:
            organization_id: Organization UUID
            key: Space key to check
            exclude_id: Optional space ID to exclude from check

        Returns:
            True if space exists, False otherwise
        """
        query = select(SpaceModel).where(
            SpaceModel.organization_id == organization_id,
            SpaceModel.key == key.upper(),
            SpaceModel.deleted_at.is_(None),
        )

        if exclude_id:
            query = query.where(SpaceModel.id != exclude_id)

        result = await self._session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_all(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
    ) -> list[Space]:
        """Get all spaces in an organization with pagination.

        Args:
            organization_id: Organization UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted spaces

        Returns:
            List of spaces
        """
        query = select(SpaceModel).where(SpaceModel.organization_id == organization_id)

        if not include_deleted:
            query = query.where(SpaceModel.deleted_at.is_(None))

        query = query.offset(skip).limit(limit).order_by(SpaceModel.created_at.desc())

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count(self, organization_id: UUID, include_deleted: bool = False) -> int:
        """Count total spaces in an organization.

        Args:
            organization_id: Organization UUID
            include_deleted: Whether to include soft-deleted spaces

        Returns:
            Total count of spaces
        """
        query = (
            select(func.count())
            .select_from(SpaceModel)
            .where(SpaceModel.organization_id == organization_id)
        )

        if not include_deleted:
            query = query.where(SpaceModel.deleted_at.is_(None))

        result = await self._session.execute(query)
        count: int = result.scalar_one()
        return count

    async def search(
        self,
        organization_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Space]:
        """Search spaces by name or key within an organization.

        Args:
            organization_id: Organization UUID
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching spaces
        """
        search_pattern = f"%{query}%"

        stmt = select(SpaceModel).where(
            SpaceModel.organization_id == organization_id,
            SpaceModel.deleted_at.is_(None),
            or_(
                SpaceModel.name.ilike(search_pattern),
                SpaceModel.key.ilike(search_pattern),
            ),
        )

        stmt = stmt.offset(skip).limit(limit).order_by(SpaceModel.name)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: SpaceModel) -> Space:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: SQLAlchemy SpaceModel

        Returns:
            Space domain entity
        """
        settings = json.loads(model.settings) if model.settings else None

        return Space(
            id=model.id,
            organization_id=model.organization_id,
            name=model.name,
            key=model.key,
            description=model.description,
            settings=settings,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
