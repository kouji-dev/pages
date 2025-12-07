"""Page repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Page


class PageRepository(ABC):
    """Abstract page repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, page: Page) -> Page:
        """Create a new page.

        Args:
            page: Page entity to create

        Returns:
            Created page with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, page_id: UUID) -> Page | None:
        """Get page by ID.

        Args:
            page_id: Page UUID

        Returns:
            Page if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_slug(self, space_id: UUID, slug: str) -> Page | None:
        """Get page by slug within a space.

        Args:
            space_id: Space UUID
            slug: Page slug

        Returns:
            Page if found, None otherwise
        """
        ...

    @abstractmethod
    async def update(self, page: Page) -> Page:
        """Update an existing page.

        Args:
            page: Page entity with updated data

        Returns:
            Updated page

        Raises:
            EntityNotFoundException: If page not found
        """
        ...

    @abstractmethod
    async def delete(self, page_id: UUID) -> None:
        """Hard delete a page.

        Args:
            page_id: Page UUID

        Raises:
            EntityNotFoundException: If page not found
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    async def get_children(self, parent_id: UUID) -> list[Page]:
        """Get all child pages of a parent page.

        Args:
            parent_id: Parent page UUID

        Returns:
            List of child pages ordered by position
        """
        ...

    @abstractmethod
    async def get_tree(self, space_id: UUID) -> list[Page]:
        """Get all pages in a space as a tree structure.

        Args:
            space_id: Space UUID

        Returns:
            List of all pages in the space (ordered for tree rendering)
        """
        ...
