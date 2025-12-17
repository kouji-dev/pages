"""Get custom field use case."""

from uuid import UUID

import structlog

from src.application.dtos.custom_field import CustomFieldResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.custom_field_repository import CustomFieldRepository

logger = structlog.get_logger()


class GetCustomFieldUseCase:
    """Use case for getting a custom field."""

    def __init__(self, custom_field_repository: CustomFieldRepository) -> None:
        """Initialize use case with dependencies."""
        self._custom_field_repository = custom_field_repository

    async def execute(self, custom_field_id: UUID) -> CustomFieldResponse:
        """Execute get custom field."""
        logger.info("Getting custom field", field_id=str(custom_field_id))

        custom_field = await self._custom_field_repository.get_by_id(custom_field_id)

        if custom_field is None:
            logger.warning("Custom field not found", field_id=str(custom_field_id))
            raise EntityNotFoundException("CustomField", str(custom_field_id))

        return CustomFieldResponse.model_validate(
            {
                "id": custom_field.id,
                "project_id": custom_field.project_id,
                "name": custom_field.name,
                "type": custom_field.type,
                "is_required": custom_field.is_required,
                "default_value": custom_field.default_value,
                "options": custom_field.options,
                "created_at": custom_field.created_at,
                "updated_at": custom_field.updated_at,
            }
        )
