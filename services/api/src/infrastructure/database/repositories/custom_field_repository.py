"""SQLAlchemy implementation of CustomFieldRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.custom_field import CustomField, CustomFieldValue
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.custom_field_repository import (
    CustomFieldRepository,
    CustomFieldValueRepository,
)
from src.infrastructure.database.models.custom_field import (
    CustomFieldModel,
    CustomFieldValueModel,
)


class SQLAlchemyCustomFieldRepository(CustomFieldRepository):
    """SQLAlchemy implementation of CustomFieldRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    async def create(self, custom_field: CustomField) -> CustomField:
        """Create a new custom field in the database."""
        model = CustomFieldModel(
            id=custom_field.id,
            project_id=custom_field.project_id,
            name=custom_field.name,
            type=custom_field.type,
            is_required=custom_field.is_required,
            default_value=custom_field.default_value,
            options=custom_field.options,
            created_at=custom_field.created_at,
            updated_at=custom_field.updated_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, custom_field_id: UUID) -> CustomField | None:
        """Get custom field by ID."""
        result = await self._session.execute(
            select(CustomFieldModel).where(CustomFieldModel.id == custom_field_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_project_id(self, project_id: UUID) -> list[CustomField]:
        """Get all custom fields for a project."""
        result = await self._session.execute(
            select(CustomFieldModel).where(CustomFieldModel.project_id == project_id)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def update(self, custom_field: CustomField) -> CustomField:
        """Update an existing custom field."""
        result = await self._session.execute(
            select(CustomFieldModel).where(CustomFieldModel.id == custom_field.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("CustomField", str(custom_field.id))

        model.name = custom_field.name
        model.type = custom_field.type
        model.is_required = custom_field.is_required
        model.default_value = custom_field.default_value
        model.options = custom_field.options
        model.updated_at = custom_field.updated_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, custom_field_id: UUID) -> None:
        """Delete a custom field."""
        result = await self._session.execute(
            select(CustomFieldModel).where(CustomFieldModel.id == custom_field_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("CustomField", str(custom_field_id))

        await self._session.delete(model)
        await self._session.flush()

    def _to_entity(self, model: CustomFieldModel) -> CustomField:
        """Convert CustomFieldModel to CustomField entity."""
        return CustomField(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            type=model.type,
            is_required=model.is_required,
            default_value=model.default_value,
            options=model.options,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SQLAlchemyCustomFieldValueRepository(CustomFieldValueRepository):
    """SQLAlchemy implementation of CustomFieldValueRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    async def create(self, value: CustomFieldValue) -> CustomFieldValue:
        """Create a new custom field value in the database."""
        model = CustomFieldValueModel(
            id=value.id,
            custom_field_id=value.custom_field_id,
            issue_id=value.issue_id,
            value=value.value,
            created_at=value.created_at,
            updated_at=value.updated_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_issue_id(self, issue_id: UUID) -> list[CustomFieldValue]:
        """Get all custom field values for an issue."""
        result = await self._session.execute(
            select(CustomFieldValueModel).where(CustomFieldValueModel.issue_id == issue_id)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_by_custom_field_id(self, custom_field_id: UUID) -> list[CustomFieldValue]:
        """Get all values for a custom field."""
        result = await self._session.execute(
            select(CustomFieldValueModel).where(
                CustomFieldValueModel.custom_field_id == custom_field_id
            )
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_by_issue_and_field(
        self, issue_id: UUID, custom_field_id: UUID
    ) -> CustomFieldValue | None:
        """Get a specific custom field value for an issue."""
        result = await self._session.execute(
            select(CustomFieldValueModel).where(
                CustomFieldValueModel.issue_id == issue_id,
                CustomFieldValueModel.custom_field_id == custom_field_id,
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def update(self, value: CustomFieldValue) -> CustomFieldValue:
        """Update an existing custom field value."""
        result = await self._session.execute(
            select(CustomFieldValueModel).where(CustomFieldValueModel.id == value.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("CustomFieldValue", str(value.id))

        model.value = value.value
        model.updated_at = value.updated_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, value_id: UUID) -> None:
        """Delete a custom field value."""
        result = await self._session.execute(
            select(CustomFieldValueModel).where(CustomFieldValueModel.id == value_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("CustomFieldValue", str(value_id))

        await self._session.delete(model)
        await self._session.flush()

    async def delete_by_issue_id(self, issue_id: UUID) -> None:
        """Delete all custom field values for an issue."""
        result = await self._session.execute(
            select(CustomFieldValueModel).where(CustomFieldValueModel.issue_id == issue_id)
        )
        models = result.scalars().all()

        for model in models:
            await self._session.delete(model)

        await self._session.flush()

    def _to_entity(self, model: CustomFieldValueModel) -> CustomFieldValue:
        """Convert CustomFieldValueModel to CustomFieldValue entity."""
        return CustomFieldValue(
            id=model.id,
            custom_field_id=model.custom_field_id,
            issue_id=model.issue_id,
            value=model.value,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
