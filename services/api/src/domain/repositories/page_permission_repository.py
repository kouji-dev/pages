"""Page and space permission repository interfaces (ports)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import PagePermission, SpacePermission


class PagePermissionRepository(ABC):
    """Abstract page permission repository interface."""

    @abstractmethod
    async def create(self, permission: PagePermission) -> PagePermission:
        """Create a new page permission.

        Args:
            permission: PagePermission entity to create

        Returns:
            Created permission with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, permission_id: UUID) -> PagePermission | None:
        """Get page permission by ID.

        Args:
            permission_id: PagePermission UUID

        Returns:
            PagePermission if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_page_and_user(
        self, page_id: UUID, user_id: UUID | None
    ) -> PagePermission | None:
        """Get page permission by page ID and user ID.

        Args:
            page_id: Page UUID
            user_id: User UUID (None for public permissions)

        Returns:
            PagePermission if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_all_by_page(self, page_id: UUID) -> list[PagePermission]:
        """Get all permissions for a page.

        Args:
            page_id: Page UUID

        Returns:
            List of page permissions
        """
        ...

    @abstractmethod
    async def update(self, permission: PagePermission) -> PagePermission:
        """Update an existing page permission.

        Args:
            permission: PagePermission entity with updated data

        Returns:
            Updated permission

        Raises:
            EntityNotFoundException: If permission not found
        """
        ...

    @abstractmethod
    async def delete(self, permission_id: UUID) -> None:
        """Delete a page permission.

        Args:
            permission_id: PagePermission UUID

        Raises:
            EntityNotFoundException: If permission not found
        """
        ...

    @abstractmethod
    async def delete_by_page_and_user(self, page_id: UUID, user_id: UUID | None) -> None:
        """Delete page permission by page ID and user ID.

        Args:
            page_id: Page UUID
            user_id: User UUID (None for public permissions)
        """
        ...


class SpacePermissionRepository(ABC):
    """Abstract space permission repository interface."""

    @abstractmethod
    async def create(self, permission: SpacePermission) -> SpacePermission:
        """Create a new space permission.

        Args:
            permission: SpacePermission entity to create

        Returns:
            Created permission with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, permission_id: UUID) -> SpacePermission | None:
        """Get space permission by ID.

        Args:
            permission_id: SpacePermission UUID

        Returns:
            SpacePermission if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_space_and_user(
        self, space_id: UUID, user_id: UUID | None
    ) -> SpacePermission | None:
        """Get space permission by space ID and user ID.

        Args:
            space_id: Space UUID
            user_id: User UUID (None for public permissions)

        Returns:
            SpacePermission if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_all_by_space(self, space_id: UUID) -> list[SpacePermission]:
        """Get all permissions for a space.

        Args:
            space_id: Space UUID

        Returns:
            List of space permissions
        """
        ...

    @abstractmethod
    async def update(self, permission: SpacePermission) -> SpacePermission:
        """Update an existing space permission.

        Args:
            permission: SpacePermission entity with updated data

        Returns:
            Updated permission

        Raises:
            EntityNotFoundException: If permission not found
        """
        ...

    @abstractmethod
    async def delete(self, permission_id: UUID) -> None:
        """Delete a space permission.

        Args:
            permission_id: SpacePermission UUID

        Raises:
            EntityNotFoundException: If permission not found
        """
        ...

    @abstractmethod
    async def delete_by_space_and_user(self, space_id: UUID, user_id: UUID | None) -> None:
        """Delete space permission by space ID and user ID.

        Args:
            space_id: Space UUID
            user_id: User UUID (None for public permissions)
        """
        ...
