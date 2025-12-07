"""SQLAlchemy implementation of TemplateRepository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Template
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import TemplateRepository
from src.infrastructure.database.models import TemplateModel


class SQLAlchemyTemplateRepository(TemplateRepository):
    """SQLAlchemy implementation of TemplateRepository.

    Adapts the domain TemplateRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, template: Template) -> Template:
        """Create a new template in the database.

        Args:
            template: Template domain entity

        Returns:
            Created template with persisted data
        """
        # Create model from entity
        model = TemplateModel(
            id=template.id,
            organization_id=template.organization_id,
            name=template.name,
            description=template.description,
            content=template.content,
            is_default=template.is_default,
            created_by=template.created_by,
            created_at=template.created_at,
            updated_at=template.updated_at,
            deleted_at=template.deleted_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, template_id: UUID) -> Template | None:
        """Get template by ID.

        Args:
            template_id: Template UUID

        Returns:
            Template if found, None otherwise
        """
        result = await self._session.execute(
            select(TemplateModel).where(TemplateModel.id == template_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def update(self, template: Template) -> Template:
        """Update an existing template.

        Args:
            template: Template entity with updated data

        Returns:
            Updated template

        Raises:
            EntityNotFoundException: If template not found
        """
        result = await self._session.execute(
            select(TemplateModel).where(TemplateModel.id == template.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Template", str(template.id))

        # Update model fields
        model.organization_id = template.organization_id
        model.name = template.name
        model.description = template.description
        model.content = template.content
        model.is_default = template.is_default
        model.updated_at = template.updated_at
        model.deleted_at = template.deleted_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, template_id: UUID) -> None:
        """Hard delete a template.

        Args:
            template_id: Template UUID

        Raises:
            EntityNotFoundException: If template not found
        """
        result = await self._session.execute(
            select(TemplateModel).where(TemplateModel.id == template_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Template", str(template_id))

        await self._session.delete(model)
        await self._session.flush()

    async def get_all(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
        include_defaults: bool = True,
    ) -> list[Template]:
        """Get all templates in an organization with pagination.

        Args:
            organization_id: Organization UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted templates
            include_defaults: Whether to include default templates

        Returns:
            List of templates
        """
        query = select(TemplateModel).where(TemplateModel.organization_id == organization_id)

        if not include_deleted:
            query = query.where(TemplateModel.deleted_at.is_(None))

        if not include_defaults:
            query = query.where(TemplateModel.is_default == False)  # noqa: E712

        query = (
            query.offset(skip)
            .limit(limit)
            .order_by(TemplateModel.is_default.desc(), TemplateModel.created_at.desc())
        )

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count(
        self,
        organization_id: UUID,
        include_deleted: bool = False,
        include_defaults: bool = True,
    ) -> int:
        """Count total templates in an organization.

        Args:
            organization_id: Organization UUID
            include_deleted: Whether to include soft-deleted templates
            include_defaults: Whether to include default templates

        Returns:
            Total count of templates
        """
        query = (
            select(func.count())
            .select_from(TemplateModel)
            .where(TemplateModel.organization_id == organization_id)
        )

        if not include_deleted:
            query = query.where(TemplateModel.deleted_at.is_(None))

        if not include_defaults:
            query = query.where(TemplateModel.is_default == False)  # noqa: E712

        result = await self._session.execute(query)
        count: int = result.scalar_one()
        return count

    def _to_entity(self, model: TemplateModel) -> Template:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: SQLAlchemy TemplateModel

        Returns:
            Template domain entity
        """
        return Template(
            id=model.id,
            organization_id=model.organization_id,
            name=model.name,
            description=model.description,
            content=model.content,
            is_default=model.is_default,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
