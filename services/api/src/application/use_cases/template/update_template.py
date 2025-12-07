"""Update template use case."""

from uuid import UUID

import structlog

from src.application.dtos.template import TemplateResponse, UpdateTemplateRequest
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import TemplateRepository

logger = structlog.get_logger()


class UpdateTemplateUseCase:
    """Use case for updating a template."""

    def __init__(self, template_repository: TemplateRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            template_repository: Template repository
        """
        self._template_repository = template_repository

    async def execute(self, template_id: str, request: UpdateTemplateRequest) -> TemplateResponse:
        """Execute update template.

        Args:
            template_id: Template ID
            request: Template update request

        Returns:
            Updated template response DTO

        Raises:
            EntityNotFoundException: If template not found
        """
        logger.info("Updating template", template_id=template_id)

        template_uuid = UUID(template_id)
        template = await self._template_repository.get_by_id(template_uuid)

        if template is None:
            logger.warning("Template not found for update", template_id=template_id)
            raise EntityNotFoundException("Template", template_id)

        # Update fields if provided
        if request.name is not None:
            template.update_name(request.name)

        if request.description is not None:
            template.update_description(request.description)

        if request.content is not None:
            template.update_content(request.content)

        if request.is_default is not None:
            template.is_default = request.is_default
            template._touch()

        # Persist changes
        updated_template = await self._template_repository.update(template)

        logger.info("Template updated", template_id=template_id)

        return TemplateResponse(
            id=updated_template.id,
            organization_id=updated_template.organization_id,
            name=updated_template.name,
            description=updated_template.description,
            content=updated_template.content,
            is_default=updated_template.is_default,
            created_by=updated_template.created_by,
            created_at=updated_template.created_at,
            updated_at=updated_template.updated_at,
        )
