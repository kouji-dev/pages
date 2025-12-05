"""SQLAlchemy implementation of OrganizationRepository."""

import json
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Organization
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import OrganizationRepository
from src.infrastructure.database.models import OrganizationMemberModel, OrganizationModel


class SQLAlchemyOrganizationRepository(OrganizationRepository):
    """SQLAlchemy implementation of OrganizationRepository.

    Adapts the domain OrganizationRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, organization: Organization) -> Organization:
        """Create a new organization in the database.

        Args:
            organization: Organization domain entity

        Returns:
            Created organization with persisted data

        Raises:
            ConflictException: If slug already exists
        """
        # Check for existing slug
        if await self.exists_by_slug(organization.slug):
            raise ConflictException(
                f"Organization with slug '{organization.slug}' already exists", field="slug"
            )

        # Create model from entity
        model = OrganizationModel(
            id=organization.id,
            name=organization.name,
            slug=organization.slug,
            description=organization.description,
            settings=json.dumps(organization.settings) if organization.settings else None,
            created_at=organization.created_at,
            updated_at=organization.updated_at,
            deleted_at=organization.deleted_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, organization_id: UUID) -> Organization | None:
        """Get organization by ID.

        Args:
            organization_id: Organization UUID

        Returns:
            Organization if found, None otherwise
        """
        result = await self._session.execute(
            select(OrganizationModel).where(OrganizationModel.id == organization_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_slug(self, slug: str) -> Organization | None:
        """Get organization by slug.

        Args:
            slug: Organization slug

        Returns:
            Organization if found, None otherwise
        """
        result = await self._session.execute(
            select(OrganizationModel).where(OrganizationModel.slug == slug)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def update(self, organization: Organization) -> Organization:
        """Update an existing organization.

        Args:
            organization: Organization entity with updated data

        Returns:
            Updated organization

        Raises:
            EntityNotFoundException: If organization not found
            ConflictException: If slug conflicts with another organization
        """
        result = await self._session.execute(
            select(OrganizationModel).where(OrganizationModel.id == organization.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Organization", str(organization.id))

        # Check for slug conflict if slug changed
        if model.slug != organization.slug:
            if await self.exists_by_slug(organization.slug, exclude_id=organization.id):
                raise ConflictException(
                    f"Organization with slug '{organization.slug}' already exists", field="slug"
                )

        # Update model fields
        model.name = organization.name
        model.slug = organization.slug
        model.description = organization.description
        model.settings = json.dumps(organization.settings) if organization.settings else None
        model.updated_at = organization.updated_at
        model.deleted_at = organization.deleted_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, organization_id: UUID) -> None:
        """Hard delete an organization.

        Args:
            organization_id: Organization UUID

        Raises:
            EntityNotFoundException: If organization not found
        """
        result = await self._session.execute(
            select(OrganizationModel).where(OrganizationModel.id == organization_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Organization", str(organization_id))

        await self._session.delete(model)
        await self._session.flush()

    async def exists_by_slug(self, slug: str, exclude_id: UUID | None = None) -> bool:
        """Check if organization with slug exists.

        Args:
            slug: Slug to check
            exclude_id: Optional organization ID to exclude from check

        Returns:
            True if organization exists, False otherwise
        """
        query = select(OrganizationModel).where(OrganizationModel.slug == slug)

        if exclude_id:
            query = query.where(OrganizationModel.id != exclude_id)

        result = await self._session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
        user_id: UUID | None = None,
    ) -> list[Organization]:
        """Get all organizations with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted organizations
            user_id: Optional user ID to filter organizations by membership

        Returns:
            List of organizations
        """
        query = select(OrganizationModel)

        if not include_deleted:
            query = query.where(OrganizationModel.deleted_at.is_(None))

        if user_id:
            query = query.join(OrganizationMemberModel).where(
                OrganizationMemberModel.user_id == user_id
            )

        query = query.offset(skip).limit(limit).order_by(OrganizationModel.created_at.desc())

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count(self, include_deleted: bool = False, user_id: UUID | None = None) -> int:
        """Count total organizations.

        Args:
            include_deleted: Whether to include soft-deleted organizations
            user_id: Optional user ID to count only organizations where user is a member

        Returns:
            Total count of organizations
        """
        query = select(func.count()).select_from(OrganizationModel)

        if not include_deleted:
            query = query.where(OrganizationModel.deleted_at.is_(None))

        if user_id:
            query = query.join(OrganizationMemberModel).where(
                OrganizationMemberModel.user_id == user_id
            )

        result = await self._session.execute(query)
        count: int = result.scalar_one()
        return count

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
        user_id: UUID | None = None,
    ) -> list[Organization]:
        """Search organizations by name or slug.

        Args:
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return
            user_id: Optional user ID to filter organizations by membership

        Returns:
            List of matching organizations
        """
        search_pattern = f"%{query}%"

        stmt = select(OrganizationModel).where(
            OrganizationModel.deleted_at.is_(None),
            or_(
                OrganizationModel.name.ilike(search_pattern),
                OrganizationModel.slug.ilike(search_pattern),
            ),
        )

        if user_id:
            stmt = stmt.join(OrganizationMemberModel).where(
                OrganizationMemberModel.user_id == user_id
            )

        stmt = stmt.offset(skip).limit(limit).order_by(OrganizationModel.name)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: OrganizationModel) -> Organization:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: SQLAlchemy OrganizationModel

        Returns:
            Organization domain entity
        """
        settings = json.loads(model.settings) if model.settings else None

        return Organization(
            id=model.id,
            name=model.name,
            slug=model.slug,
            description=model.description,
            settings=settings,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
