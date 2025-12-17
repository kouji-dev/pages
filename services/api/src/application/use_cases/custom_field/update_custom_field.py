"""Update custom field use case."""

from uuid import UUID

import structlog

from src.application.dtos.custom_field import (
    CustomFieldResponse,
    UpdateCustomFieldRequest,
)
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories.custom_field_repository import CustomFieldRepository

logger = structlog.get_logger()


class UpdateCustomFieldUseCase:
    """Use case for updating a custom field."""

    def __init__(self, custom_field_repository: CustomFieldRepository) -> None:
        """Initialize use case with dependencies."""
        self._custom_field_repository = custom_field_repository

    async def execute(
        self, custom_field_id: UUID, request: "UpdateCustomFieldRequest"
    ) -> CustomFieldResponse:
        """Execute update custom field."""
        logger.info("Updating custom field", field_id=str(custom_field_id))

        custom_field = await self._custom_field_repository.get_by_id(custom_field_id)

        if custom_field is None:
            logger.warning("Custom field not found", field_id=str(custom_field_id))
            raise EntityNotFoundException("CustomField", str(custom_field_id))

        # Apply updates
        if request.name is not None:
            try:
                custom_field.update_name(request.name)
            except ValueError as e:
                raise ValidationException(str(e), field="name") from e

        # Note: type is not updatable in UpdateCustomFieldRequest

        if request.is_required is not None:
            custom_field.is_required = request.is_required
            custom_field._touch()

        if request.default_value is not None:
            custom_field.default_value = request.default_value
            custom_field._touch()

        if request.options is not None:
            try:
                custom_field.update_options(request.options)
            except ValueError as e:
                raise ValidationException(str(e), field="options") from e

        # Save to database
        updated_field = await self._custom_field_repository.update(custom_field)

        logger.info("Custom field updated", field_id=str(custom_field_id))

        return CustomFieldResponse.model_validate(
            {
                "id": updated_field.id,
                "project_id": updated_field.project_id,
                "name": updated_field.name,
                "type": updated_field.type,
                "is_required": updated_field.is_required,
                "default_value": updated_field.default_value,
                "options": updated_field.options,
                "created_at": updated_field.created_at,
                "updated_at": updated_field.updated_at,
            }
        )
