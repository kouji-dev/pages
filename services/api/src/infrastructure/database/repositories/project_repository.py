"""SQLAlchemy implementation of ProjectRepository."""

import json
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Project
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import ProjectRepository
from src.infrastructure.database.models import ProjectModel


class SQLAlchemyProjectRepository(ProjectRepository):
    """SQLAlchemy implementation of ProjectRepository.

    Adapts the domain ProjectRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, project: Project) -> Project:
        """Create a new project in the database.

        Args:
            project: Project domain entity

        Returns:
            Created project with persisted data

        Raises:
            ConflictException: If project key already exists in organization
        """
        # Check for existing key in organization
        if await self.exists_by_key(project.organization_id, project.key):
            raise ConflictException(
                f"Project with key '{project.key}' already exists in this organization",
                field="key",
            )

        # Create model from entity
        model = ProjectModel(
            id=project.id,
            organization_id=project.organization_id,
            name=project.name,
            key=project.key,
            description=project.description,
            settings=json.dumps(project.settings) if project.settings else None,
            created_at=project.created_at,
            updated_at=project.updated_at,
            deleted_at=project.deleted_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, project_id: UUID) -> Project | None:
        """Get project by ID.

        Args:
            project_id: Project UUID

        Returns:
            Project if found, None otherwise
        """
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_key(self, organization_id: UUID, key: str) -> Project | None:
        """Get project by key within an organization.

        Args:
            organization_id: Organization UUID
            key: Project key

        Returns:
            Project if found, None otherwise
        """
        result = await self._session.execute(
            select(ProjectModel).where(
                ProjectModel.organization_id == organization_id,
                ProjectModel.key == key.upper(),
                ProjectModel.deleted_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def update(self, project: Project) -> Project:
        """Update an existing project.

        Args:
            project: Project entity with updated data

        Returns:
            Updated project

        Raises:
            EntityNotFoundException: If project not found
            ConflictException: If key conflicts with another project in the organization
        """
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Project", str(project.id))

        # Check for key conflict if key changed
        if model.key != project.key:
            if await self.exists_by_key(
                project.organization_id, project.key, exclude_id=project.id
            ):
                raise ConflictException(
                    f"Project with key '{project.key}' already exists in this organization",
                    field="key",
                )

        # Update model fields
        model.organization_id = project.organization_id
        model.name = project.name
        model.key = project.key
        model.description = project.description
        model.settings = json.dumps(project.settings) if project.settings else None
        model.updated_at = project.updated_at
        model.deleted_at = project.deleted_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, project_id: UUID) -> None:
        """Hard delete a project.

        Args:
            project_id: Project UUID

        Raises:
            EntityNotFoundException: If project not found
        """
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Project", str(project_id))

        await self._session.delete(model)
        await self._session.flush()

    async def exists_by_key(
        self, organization_id: UUID, key: str, exclude_id: UUID | None = None
    ) -> bool:
        """Check if project with key exists in organization.

        Args:
            organization_id: Organization UUID
            key: Project key to check
            exclude_id: Optional project ID to exclude from check

        Returns:
            True if project exists, False otherwise
        """
        query = select(ProjectModel).where(
            ProjectModel.organization_id == organization_id,
            ProjectModel.key == key.upper(),
            ProjectModel.deleted_at.is_(None),
        )

        if exclude_id:
            query = query.where(ProjectModel.id != exclude_id)

        result = await self._session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_all(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
    ) -> list[Project]:
        """Get all projects in an organization with pagination.

        Args:
            organization_id: Organization UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted projects

        Returns:
            List of projects
        """
        query = select(ProjectModel).where(ProjectModel.organization_id == organization_id)

        if not include_deleted:
            query = query.where(ProjectModel.deleted_at.is_(None))

        query = query.offset(skip).limit(limit).order_by(ProjectModel.created_at.desc())

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count(self, organization_id: UUID, include_deleted: bool = False) -> int:
        """Count total projects in an organization.

        Args:
            organization_id: Organization UUID
            include_deleted: Whether to include soft-deleted projects

        Returns:
            Total count of projects
        """
        query = (
            select(func.count())
            .select_from(ProjectModel)
            .where(ProjectModel.organization_id == organization_id)
        )

        if not include_deleted:
            query = query.where(ProjectModel.deleted_at.is_(None))

        result = await self._session.execute(query)
        count: int = result.scalar_one()
        return count

    async def search(
        self,
        organization_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Project]:
        """Search projects by name or key within an organization.

        Args:
            organization_id: Organization UUID
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching projects
        """
        search_pattern = f"%{query}%"

        stmt = select(ProjectModel).where(
            ProjectModel.organization_id == organization_id,
            ProjectModel.deleted_at.is_(None),
            or_(
                ProjectModel.name.ilike(search_pattern),
                ProjectModel.key.ilike(search_pattern),
            ),
        )

        stmt = stmt.offset(skip).limit(limit).order_by(ProjectModel.name)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: ProjectModel) -> Project:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: SQLAlchemy ProjectModel

        Returns:
            Project domain entity
        """
        settings = json.loads(model.settings) if model.settings else None

        return Project(
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
