"""Create custom field use case."""

from uuid import UUID

import structlog

from src.application.dtos.custom_field import CustomFieldRequest, CustomFieldResponse
from src.domain.entities.custom_field import CustomField
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import ProjectRepository
from src.domain.repositories.custom_field_repository import CustomFieldRepository

logger = structlog.get_logger()


class CreateCustomFieldUseCase:
    """Use case for creating a custom field."""

    def __init__(
        self,
        custom_field_repository: CustomFieldRepository,
        project_repository: ProjectRepository,
    ) -> None:
        """Initialize use case with dependencies."""
        self._custom_field_repository = custom_field_repository
        self._project_repository = project_repository

    async def execute(self, project_id: UUID, request: CustomFieldRequest) -> CustomFieldResponse:
        """Execute create custom field."""
        logger.info("Creating custom field", project_id=str(project_id), name=request.name)

        # Verify project exists
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            logger.warning("Project not found", project_id=str(project_id))
            raise EntityNotFoundException("Project", str(project_id))

        # Create custom field entity
        try:
            custom_field = CustomField.create(
                project_id=project_id,
                name=request.name,
                type=request.type,
                is_required=request.is_required,
                default_value=request.default_value,
                options=request.options,
            )
        except ValueError as e:
            raise ValidationException(str(e), field="custom_field") from e

        # Save to database
        created_field = await self._custom_field_repository.create(custom_field)

        logger.info("Custom field created", field_id=str(created_field.id))

        # Convert to response DTO
        return CustomFieldResponse.model_validate(
            {
                "id": created_field.id,
                "project_id": created_field.project_id,
                "name": created_field.name,
                "type": created_field.type,
                "is_required": created_field.is_required,
                "default_value": created_field.default_value,
                "options": created_field.options,
                "created_at": created_field.created_at,
                "updated_at": created_field.updated_at,
            }
        )
