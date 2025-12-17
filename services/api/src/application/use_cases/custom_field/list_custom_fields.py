"""List custom fields use case."""

from uuid import UUID

import structlog

from src.application.dtos.custom_field import CustomFieldListResponse, CustomFieldResponse
from src.domain.repositories.custom_field_repository import CustomFieldRepository

logger = structlog.get_logger()


class ListCustomFieldsUseCase:
    """Use case for listing custom fields."""

    def __init__(self, custom_field_repository: CustomFieldRepository) -> None:
        """Initialize use case with dependencies."""
        self._custom_field_repository = custom_field_repository

    async def execute(self, project_id: UUID) -> CustomFieldListResponse:
        """Execute list custom fields."""
        logger.info("Listing custom fields", project_id=str(project_id))

        fields = await self._custom_field_repository.get_by_project_id(project_id)

        # Convert to response DTOs
        field_items = [
            CustomFieldResponse.model_validate(
                {
                    "id": f.id,
                    "project_id": f.project_id,
                    "name": f.name,
                    "type": f.type,
                    "is_required": f.is_required,
                    "default_value": f.default_value,
                    "options": f.options,
                    "created_at": f.created_at,
                    "updated_at": f.updated_at,
                }
            )
            for f in fields
        ]

        return CustomFieldListResponse(fields=field_items, total=len(field_items))
