"""Folder repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Folder


class FolderRepository(ABC):
    """Abstract folder repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, folder: Folder) -> Folder:
        """Create a new folder.

        Args:
            folder: Folder entity to create

        Returns:
            Created folder with persisted data

        Raises:
            ConflictException: If folder name conflicts in organization
        """
        ...

    @abstractmethod
    async def get_by_id(self, folder_id: UUID) -> Folder | None:
        """Get folder by ID.

        Args:
            folder_id: Folder UUID

        Returns:
            Folder if found, None otherwise
        """
        ...

    @abstractmethod
    async def update(self, folder: Folder) -> Folder:
        """Update an existing folder.

        Args:
            folder: Folder entity with updated data

        Returns:
            Updated folder

        Raises:
            EntityNotFoundException: If folder not found
        """
        ...

    @abstractmethod
    async def delete(self, folder_id: UUID) -> None:
        """Hard delete a folder.

        Args:
            folder_id: Folder UUID

        Raises:
            EntityNotFoundException: If folder not found
        """
        ...

    @abstractmethod
    async def get_all(
        self,
        organization_id: UUID,
        parent_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[Folder]:
        """Get all folders in an organization with optional filtering.

        Args:
            organization_id: Organization UUID
            parent_id: Optional parent folder ID to filter by (None for root folders)
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted folders

        Returns:
            List of folders
        """
        ...

    @abstractmethod
    async def count(
        self,
        organization_id: UUID,
        parent_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> int:
        """Count total folders in an organization.

        Args:
            organization_id: Organization UUID
            parent_id: Optional parent folder ID to filter by
            include_deleted: Whether to include soft-deleted folders

        Returns:
            Total count of folders
        """
        ...

    @abstractmethod
    async def get_children(self, folder_id: UUID) -> list[Folder]:
        """Get all child folders of a folder.

        Args:
            folder_id: Parent folder UUID

        Returns:
            List of child folders
        """
        ...

    @abstractmethod
    async def exists_by_name(
        self,
        organization_id: UUID,
        name: str,
        parent_id: UUID | None = None,
        exclude_id: UUID | None = None,
    ) -> bool:
        """Check if folder with name exists in organization/parent.

        Args:
            organization_id: Organization UUID
            name: Folder name to check
            parent_id: Optional parent folder ID
            exclude_id: Optional folder ID to exclude from check

        Returns:
            True if folder exists, False otherwise
        """
        ...

