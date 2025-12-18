"""SQLAlchemy implementation of PageVersionRepository."""

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import PageVersion
from src.domain.repositories import PageVersionRepository
from src.infrastructure.database.models import PageVersionModel


class SQLAlchemyPageVersionRepository(PageVersionRepository):
    """SQLAlchemy implementation of PageVersionRepository.

    Adapts the domain PageVersionRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, page_version: PageVersion) -> PageVersion:
        """Create a new page version in the database.

        Args:
            page_version: PageVersion domain entity

        Returns:
            Created page version with persisted data
        """
        # Create model from entity
        model = PageVersionModel(
            id=page_version.id,
            page_id=page_version.page_id,
            version_number=page_version.version_number,
            title=page_version.title,
            content=page_version.content,
            created_by=page_version.created_by,
            created_at=page_version.created_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, version_id: UUID) -> PageVersion | None:
        """Get page version by ID.

        Args:
            version_id: PageVersion UUID

        Returns:
            PageVersion if found, None otherwise
        """
        result = await self._session.execute(
            select(PageVersionModel).where(PageVersionModel.id == version_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_page_and_version(
        self, page_id: UUID, version_number: int
    ) -> PageVersion | None:
        """Get page version by page ID and version number.

        Args:
            page_id: Page UUID
            version_number: Version number

        Returns:
            PageVersion if found, None otherwise
        """
        result = await self._session.execute(
            select(PageVersionModel).where(
                PageVersionModel.page_id == page_id,
                PageVersionModel.version_number == version_number,
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_all(
        self,
        page_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[PageVersion]:
        """Get all versions for a page with pagination.

        Args:
            page_id: Page UUID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of page versions ordered by version_number descending
        """
        result = await self._session.execute(
            select(PageVersionModel)
            .where(PageVersionModel.page_id == page_id)
            .order_by(PageVersionModel.version_number.desc())
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count(self, page_id: UUID) -> int:
        """Count total versions for a page.

        Args:
            page_id: Page UUID

        Returns:
            Total count of versions
        """
        result = await self._session.execute(
            select(func.count(PageVersionModel.id)).where(PageVersionModel.page_id == page_id)
        )
        return result.scalar_one() or 0

    async def get_latest_version(self, page_id: UUID) -> PageVersion | None:
        """Get the latest version for a page.

        Args:
            page_id: Page UUID

        Returns:
            Latest PageVersion if found, None otherwise
        """
        result = await self._session.execute(
            select(PageVersionModel)
            .where(PageVersionModel.page_id == page_id)
            .order_by(PageVersionModel.version_number.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_next_version_number(self, page_id: UUID) -> int:
        """Get the next version number for a page.

        Args:
            page_id: Page UUID

        Returns:
            Next version number (1 if no versions exist)
        """
        result = await self._session.execute(
            select(func.max(PageVersionModel.version_number)).where(
                PageVersionModel.page_id == page_id
            )
        )
        max_version = result.scalar_one()

        if max_version is None:
            return 1

        return max_version + 1

    async def delete_old_versions(self, page_id: UUID, keep_count: int) -> int:
        """Delete old versions, keeping only the most recent N versions.

        Args:
            page_id: Page UUID
            keep_count: Number of recent versions to keep

        Returns:
            Number of versions deleted
        """
        # Get versions to keep
        result = await self._session.execute(
            select(PageVersionModel.version_number)
            .where(PageVersionModel.page_id == page_id)
            .order_by(PageVersionModel.version_number.desc())
            .limit(keep_count)
        )
        versions_to_keep = {row[0] for row in result.all()}

        # Delete versions not in the keep list
        if versions_to_keep:
            result = await self._session.execute(
                delete(PageVersionModel).where(
                    PageVersionModel.page_id == page_id,
                    ~PageVersionModel.version_number.in_(versions_to_keep),
                )
            )
        else:
            # If no versions to keep, delete all
            result = await self._session.execute(
                delete(PageVersionModel).where(PageVersionModel.page_id == page_id)
            )

        # Get rowcount (SQLAlchemy 2.0 returns it as an attribute)
        rowcount = getattr(result, "rowcount", 0) or 0
        return int(rowcount)

    def _to_entity(self, model: PageVersionModel) -> PageVersion:
        """Convert database model to domain entity.

        Args:
            model: PageVersionModel instance

        Returns:
            PageVersion domain entity
        """
        return PageVersion(
            id=model.id,
            page_id=model.page_id,
            version_number=model.version_number,
            title=model.title,
            content=model.content,
            created_by=model.created_by,
            created_at=model.created_at,
        )
