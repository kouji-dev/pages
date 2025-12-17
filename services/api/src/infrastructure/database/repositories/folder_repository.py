"""SQLAlchemy implementation of FolderRepository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Folder
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import FolderRepository
from src.infrastructure.database.models import FolderModel


class SQLAlchemyFolderRepository(FolderRepository):
    """SQLAlchemy implementation of FolderRepository.

    Adapts the domain FolderRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, folder: Folder) -> Folder:
        """Create a new folder in the database.

        Args:
            folder: Folder domain entity

        Returns:
            Created folder with persisted data

        Raises:
            ConflictException: If folder name conflicts in organization/parent
        """
        # Check for existing name in organization/parent
        if await self.exists_by_name(
            folder.organization_id, folder.name, folder.parent_id
        ):
            raise ConflictException(
                f"Folder with name '{folder.name}' already exists in this location",
                field="name",
            )

        # Create model from entity
        model = FolderModel(
            id=folder.id,
            organization_id=folder.organization_id,
            name=folder.name,
            parent_id=folder.parent_id,
            position=folder.position,
            created_at=folder.created_at,
            updated_at=folder.updated_at,
            deleted_at=folder.deleted_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, folder_id: UUID) -> Folder | None:
        """Get folder by ID.

        Args:
            folder_id: Folder UUID

        Returns:
            Folder if found, None otherwise
        """
        result = await self._session.execute(
            select(FolderModel).where(FolderModel.id == folder_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def update(self, folder: Folder) -> Folder:
        """Update an existing folder.

        Args:
            folder: Folder entity with updated data

        Returns:
            Updated folder

        Raises:
            EntityNotFoundException: If folder not found
            ConflictException: If name conflicts with another folder
        """
        result = await self._session.execute(
            select(FolderModel).where(FolderModel.id == folder.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Folder", str(folder.id))

        # Check for name conflict if name or parent changed
        if model.name != folder.name or model.parent_id != folder.parent_id:
            if await self.exists_by_name(
                folder.organization_id,
                folder.name,
                folder.parent_id,
                exclude_id=folder.id,
            ):
                raise ConflictException(
                    f"Folder with name '{folder.name}' already exists in this location",
                    field="name",
                )

        # Update model fields
        model.organization_id = folder.organization_id
        model.name = folder.name
        model.parent_id = folder.parent_id
        model.position = folder.position
        model.updated_at = folder.updated_at
        model.deleted_at = folder.deleted_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, folder_id: UUID) -> None:
        """Hard delete a folder.

        Args:
            folder_id: Folder UUID

        Raises:
            EntityNotFoundException: If folder not found
        """
        result = await self._session.execute(
            select(FolderModel).where(FolderModel.id == folder_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Folder", str(folder_id))

        await self._session.delete(model)
        await self._session.flush()

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
        query = select(FolderModel).where(FolderModel.organization_id == organization_id)

        if parent_id is None:
            query = query.where(FolderModel.parent_id.is_(None))
        else:
            query = query.where(FolderModel.parent_id == parent_id)

        if not include_deleted:
            query = query.where(FolderModel.deleted_at.is_(None))

        query = query.offset(skip).limit(limit).order_by(FolderModel.position, FolderModel.name)

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

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
        query = (
            select(func.count())
            .select_from(FolderModel)
            .where(FolderModel.organization_id == organization_id)
        )

        if parent_id is None:
            query = query.where(FolderModel.parent_id.is_(None))
        else:
            query = query.where(FolderModel.parent_id == parent_id)

        if not include_deleted:
            query = query.where(FolderModel.deleted_at.is_(None))

        result = await self._session.execute(query)
        count: int = result.scalar_one()
        return count

    async def get_children(self, folder_id: UUID) -> list[Folder]:
        """Get all child folders of a folder.

        Args:
            folder_id: Parent folder UUID

        Returns:
            List of child folders
        """
        query = select(FolderModel).where(
            FolderModel.parent_id == folder_id,
            FolderModel.deleted_at.is_(None),
        )

        query = query.order_by(FolderModel.position, FolderModel.name)

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

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
        query = select(FolderModel).where(
            FolderModel.organization_id == organization_id,
            FolderModel.name == name,
            FolderModel.deleted_at.is_(None),
        )

        if parent_id is None:
            query = query.where(FolderModel.parent_id.is_(None))
        else:
            query = query.where(FolderModel.parent_id == parent_id)

        if exclude_id:
            query = query.where(FolderModel.id != exclude_id)

        result = await self._session.execute(query)
        return result.scalar_one_or_none() is not None

    def _to_entity(self, model: FolderModel) -> Folder:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: SQLAlchemy FolderModel

        Returns:
            Folder domain entity
        """
        return Folder(
            id=model.id,
            organization_id=model.organization_id,
            name=model.name,
            parent_id=model.parent_id,
            position=model.position,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

