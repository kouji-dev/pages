"""Delete template use case."""

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import TemplateRepository

logger = structlog.get_logger()


class DeleteTemplateUseCase:
    """Use case for deleting a template."""

    def __init__(self, template_repository: TemplateRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            template_repository: Template repository
        """
        self._template_repository = template_repository

    async def execute(self, template_id: str) -> None:
        """Execute delete template (soft delete).

        Args:
            template_id: Template ID

        Raises:
            EntityNotFoundException: If template not found
        """
        from uuid import UUID

        logger.info("Deleting template", template_id=template_id)

        template_uuid = UUID(template_id)
        template = await self._template_repository.get_by_id(template_uuid)

        if template is None:
            logger.warning("Template not found for deletion", template_id=template_id)
            raise EntityNotFoundException("Template", template_id)

        # Soft delete
        template.delete()
        await self._template_repository.update(template)

        logger.info("Template deleted", template_id=template_id)
