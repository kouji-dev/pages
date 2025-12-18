"""Page version repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import PageVersion


class PageVersionRepository(ABC):
    """Abstract page version repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, page_version: PageVersion) -> PageVersion:
        """Create a new page version.

        Args:
            page_version: PageVersion entity to create

        Returns:
            Created page version with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, version_id: UUID) -> PageVersion | None:
        """Get page version by ID.

        Args:
            version_id: PageVersion UUID

        Returns:
            PageVersion if found, None otherwise
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    async def count(self, page_id: UUID) -> int:
        """Count total versions for a page.

        Args:
            page_id: Page UUID

        Returns:
            Total count of versions
        """
        ...

    @abstractmethod
    async def get_latest_version(self, page_id: UUID) -> PageVersion | None:
        """Get the latest version for a page.

        Args:
            page_id: Page UUID

        Returns:
            Latest PageVersion if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_next_version_number(self, page_id: UUID) -> int:
        """Get the next version number for a page.

        Args:
            page_id: Page UUID

        Returns:
            Next version number (1 if no versions exist)
        """
        ...

    @abstractmethod
    async def delete_old_versions(self, page_id: UUID, keep_count: int) -> int:
        """Delete old versions, keeping only the most recent N versions.

        Args:
            page_id: Page UUID
            keep_count: Number of recent versions to keep

        Returns:
            Number of versions deleted
        """
        ...
