"""SQLAlchemy implementation of PageRepository."""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Page
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageRepository
from src.infrastructure.database.models import PageModel


class SQLAlchemyPageRepository(PageRepository):
    """SQLAlchemy implementation of PageRepository.

    Adapts the domain PageRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, page: Page) -> Page:
        """Create a new page in the database.

        Args:
            page: Page domain entity

        Returns:
            Created page with persisted data
        """
        # Create model from entity
        model = PageModel(
            id=page.id,
            space_id=page.space_id,
            title=page.title,
            slug=page.slug,
            content=page.content,
            parent_id=page.parent_id,
            created_by=page.created_by,
            updated_by=page.updated_by,
            position=page.position,
            created_at=page.created_at,
            updated_at=page.updated_at,
            deleted_at=page.deleted_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, page_id: UUID) -> Page | None:
        """Get page by ID.

        Args:
            page_id: Page UUID

        Returns:
            Page if found, None otherwise
        """
        result = await self._session.execute(select(PageModel).where(PageModel.id == page_id))
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_slug(self, space_id: UUID, slug: str) -> Page | None:
        """Get page by slug within a space.

        Args:
            space_id: Space UUID
            slug: Page slug

        Returns:
            Page if found, None otherwise
        """
        result = await self._session.execute(
            select(PageModel).where(
                PageModel.space_id == space_id,
                PageModel.slug == slug.lower(),
                PageModel.deleted_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def update(self, page: Page) -> Page:
        """Update an existing page.

        Args:
            page: Page entity with updated data

        Returns:
            Updated page

        Raises:
            EntityNotFoundException: If page not found
        """
        result = await self._session.execute(select(PageModel).where(PageModel.id == page.id))
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Page", str(page.id))

        # Prevent circular reference
        if page.parent_id == page.id:
            raise ValueError("Page cannot be its own parent")

        # Update model fields
        model.space_id = page.space_id
        model.title = page.title
        model.slug = page.slug
        model.content = page.content
        model.parent_id = page.parent_id
        model.updated_by = page.updated_by
        model.position = page.position
        model.updated_at = page.updated_at
        model.deleted_at = page.deleted_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, page_id: UUID) -> None:
        """Hard delete a page.

        Args:
            page_id: Page UUID

        Raises:
            EntityNotFoundException: If page not found
        """
        result = await self._session.execute(select(PageModel).where(PageModel.id == page_id))
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Page", str(page_id))

        await self._session.delete(model)
        await self._session.flush()

    async def get_all(
        self,
        space_id: UUID,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
        parent_id: UUID | None = None,
    ) -> list[Page]:
        """Get all pages in a space with pagination.

        Args:
            space_id: Space UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted pages
            parent_id: Optional parent page ID to filter by (None for root pages)

        Returns:
            List of pages
        """
        query = select(PageModel).where(PageModel.space_id == space_id)

        if parent_id is None:
            query = query.where(PageModel.parent_id.is_(None))
        else:
            query = query.where(PageModel.parent_id == parent_id)

        if not include_deleted:
            query = query.where(PageModel.deleted_at.is_(None))

        query = query.order_by(PageModel.position.asc(), PageModel.created_at.asc())
        query = query.offset(skip).limit(limit)

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count(
        self,
        space_id: UUID,
        include_deleted: bool = False,
        parent_id: UUID | None = None,
    ) -> int:
        """Count total pages in a space.

        Args:
            space_id: Space UUID
            include_deleted: Whether to include soft-deleted pages
            parent_id: Optional parent page ID to filter by (None for root pages)

        Returns:
            Total count of pages
        """
        query = select(func.count()).select_from(PageModel).where(PageModel.space_id == space_id)

        if parent_id is None:
            query = query.where(PageModel.parent_id.is_(None))
        else:
            query = query.where(PageModel.parent_id == parent_id)

        if not include_deleted:
            query = query.where(PageModel.deleted_at.is_(None))

        result = await self._session.execute(query)
        count: int = result.scalar_one()
        return count

    async def search(
        self,
        space_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Page]:
        """Search pages by title or content within a space.

        Args:
            space_id: Space UUID
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching pages
        """
        search_pattern = f"%{query}%"

        stmt = select(PageModel).where(
            PageModel.space_id == space_id,
            PageModel.deleted_at.is_(None),
            or_(
                PageModel.title.ilike(search_pattern),
                PageModel.content.ilike(search_pattern),
            ),
        )

        stmt = stmt.order_by(PageModel.title).offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_children(self, parent_id: UUID) -> list[Page]:
        """Get all child pages of a parent page.

        Args:
            parent_id: Parent page UUID

        Returns:
            List of child pages ordered by position
        """
        query = (
            select(PageModel)
            .where(
                PageModel.parent_id == parent_id,
                PageModel.deleted_at.is_(None),
            )
            .order_by(PageModel.position.asc(), PageModel.created_at.asc())
        )

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_tree(self, space_id: UUID) -> list[Page]:
        """Get all pages in a space as a tree structure.

        Args:
            space_id: Space UUID

        Returns:
            List of all pages in the space (ordered for tree rendering)
        """
        query = (
            select(PageModel)
            .where(
                PageModel.space_id == space_id,
                PageModel.deleted_at.is_(None),
            )
            .order_by(
                PageModel.parent_id.asc().nullsfirst(),
                PageModel.position.asc(),
                PageModel.created_at.asc(),
            )
        )

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: PageModel) -> Page:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: SQLAlchemy PageModel

        Returns:
            Page domain entity
        """
        return Page(
            id=model.id,
            space_id=model.space_id,
            title=model.title,
            slug=model.slug,
            content=model.content,
            parent_id=model.parent_id,
            created_by=model.created_by,
            updated_by=model.updated_by,
            position=model.position,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
