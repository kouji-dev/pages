"""SQLAlchemy implementation of PagePermissionRepository and SpacePermissionRepository."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import PagePermission, SpacePermission
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    PagePermissionRepository,
    SpacePermissionRepository,
)
from src.infrastructure.database.models import (
    PagePermissionModel,
    SpacePermissionModel,
)


class SQLAlchemyPagePermissionRepository(PagePermissionRepository):
    """SQLAlchemy implementation of PagePermissionRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, permission: PagePermission) -> PagePermission:
        """Create a new page permission in the database."""
        model = PagePermissionModel(
            id=permission.id,
            page_id=permission.page_id,
            user_id=permission.user_id,
            role=permission.role,
            inherited_from_space=permission.inherited_from_space,
            created_at=permission.created_at,
            updated_at=permission.updated_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, permission_id: UUID) -> PagePermission | None:
        """Get page permission by ID."""
        result = await self._session.execute(
            select(PagePermissionModel).where(PagePermissionModel.id == permission_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_page_and_user(
        self, page_id: UUID, user_id: UUID | None
    ) -> PagePermission | None:
        """Get page permission by page ID and user ID."""
        result = await self._session.execute(
            select(PagePermissionModel).where(
                PagePermissionModel.page_id == page_id,
                PagePermissionModel.user_id == user_id,
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_all_by_page(self, page_id: UUID) -> list[PagePermission]:
        """Get all permissions for a page."""
        result = await self._session.execute(
            select(PagePermissionModel).where(PagePermissionModel.page_id == page_id)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def update(self, permission: PagePermission) -> PagePermission:
        """Update an existing page permission."""
        result = await self._session.execute(
            select(PagePermissionModel).where(PagePermissionModel.id == permission.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("PagePermission", str(permission.id))

        model.role = permission.role
        model.inherited_from_space = permission.inherited_from_space
        model.updated_at = permission.updated_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, permission_id: UUID) -> None:
        """Delete a page permission."""
        result = await self._session.execute(
            select(PagePermissionModel).where(PagePermissionModel.id == permission_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("PagePermission", str(permission_id))

        await self._session.delete(model)
        await self._session.flush()

    async def delete_by_page_and_user(self, page_id: UUID, user_id: UUID | None) -> None:
        """Delete page permission by page ID and user ID."""
        await self._session.execute(
            delete(PagePermissionModel).where(
                PagePermissionModel.page_id == page_id,
                PagePermissionModel.user_id == user_id,
            )
        )
        await self._session.flush()

    def _to_entity(self, model: PagePermissionModel) -> PagePermission:
        """Convert database model to domain entity."""
        return PagePermission(
            id=model.id,
            page_id=model.page_id,
            user_id=model.user_id,
            role=model.role,
            inherited_from_space=model.inherited_from_space,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SQLAlchemySpacePermissionRepository(SpacePermissionRepository):
    """SQLAlchemy implementation of SpacePermissionRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, permission: SpacePermission) -> SpacePermission:
        """Create a new space permission in the database."""
        model = SpacePermissionModel(
            id=permission.id,
            space_id=permission.space_id,
            user_id=permission.user_id,
            role=permission.role,
            created_at=permission.created_at,
            updated_at=permission.updated_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, permission_id: UUID) -> SpacePermission | None:
        """Get space permission by ID."""
        result = await self._session.execute(
            select(SpacePermissionModel).where(SpacePermissionModel.id == permission_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_space_and_user(
        self, space_id: UUID, user_id: UUID | None
    ) -> SpacePermission | None:
        """Get space permission by space ID and user ID."""
        result = await self._session.execute(
            select(SpacePermissionModel).where(
                SpacePermissionModel.space_id == space_id,
                SpacePermissionModel.user_id == user_id,
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_all_by_space(self, space_id: UUID) -> list[SpacePermission]:
        """Get all permissions for a space."""
        result = await self._session.execute(
            select(SpacePermissionModel).where(SpacePermissionModel.space_id == space_id)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def update(self, permission: SpacePermission) -> SpacePermission:
        """Update an existing space permission."""
        result = await self._session.execute(
            select(SpacePermissionModel).where(SpacePermissionModel.id == permission.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("SpacePermission", str(permission.id))

        model.role = permission.role
        model.updated_at = permission.updated_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, permission_id: UUID) -> None:
        """Delete a space permission."""
        result = await self._session.execute(
            select(SpacePermissionModel).where(SpacePermissionModel.id == permission_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("SpacePermission", str(permission_id))

        await self._session.delete(model)
        await self._session.flush()

    async def delete_by_space_and_user(self, space_id: UUID, user_id: UUID | None) -> None:
        """Delete space permission by space ID and user ID."""
        await self._session.execute(
            delete(SpacePermissionModel).where(
                SpacePermissionModel.space_id == space_id,
                SpacePermissionModel.user_id == user_id,
            )
        )
        await self._session.flush()

    def _to_entity(self, model: SpacePermissionModel) -> SpacePermission:
        """Convert database model to domain entity."""
        return SpacePermission(
            id=model.id,
            space_id=model.space_id,
            user_id=model.user_id,
            role=model.role,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
