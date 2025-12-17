"""Delete custom field use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.custom_field_repository import CustomFieldRepository

logger = structlog.get_logger()


class DeleteCustomFieldUseCase:
    """Use case for deleting a custom field."""

    def __init__(self, custom_field_repository: CustomFieldRepository) -> None:
        """Initialize use case with dependencies."""
        self._custom_field_repository = custom_field_repository

    async def execute(self, custom_field_id: UUID) -> None:
        """Execute delete custom field."""
        logger.info("Deleting custom field", field_id=str(custom_field_id))

        # Verify custom field exists
        custom_field = await self._custom_field_repository.get_by_id(custom_field_id)
        if custom_field is None:
            logger.warning("Custom field not found", field_id=str(custom_field_id))
            raise EntityNotFoundException("CustomField", str(custom_field_id))

        await self._custom_field_repository.delete(custom_field_id)

        logger.info("Custom field deleted", field_id=str(custom_field_id))
