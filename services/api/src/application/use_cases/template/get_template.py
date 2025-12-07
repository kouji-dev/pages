"""Get template use case."""

from uuid import UUID

import structlog

from src.application.dtos.template import TemplateResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import TemplateRepository

logger = structlog.get_logger()


class GetTemplateUseCase:
    """Use case for retrieving a template."""

    def __init__(self, template_repository: TemplateRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            template_repository: Template repository
        """
        self._template_repository = template_repository

    async def execute(self, template_id: str) -> TemplateResponse:
        """Execute get template.

        Args:
            template_id: Template ID

        Returns:
            Template response DTO

        Raises:
            EntityNotFoundException: If template not found
        """
        logger.info("Getting template", template_id=template_id)

        template_uuid = UUID(template_id)
        template = await self._template_repository.get_by_id(template_uuid)

        if template is None:
            logger.warning("Template not found", template_id=template_id)
            raise EntityNotFoundException("Template", template_id)

        return TemplateResponse(
            id=template.id,
            organization_id=template.organization_id,
            name=template.name,
            description=template.description,
            content=template.content,
            is_default=template.is_default,
            created_by=template.created_by,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )
