"""List templates use case."""

from math import ceil
from uuid import UUID

import structlog

from src.application.dtos.template import TemplateListItemResponse, TemplateListResponse
from src.domain.repositories import TemplateRepository

logger = structlog.get_logger()


class ListTemplatesUseCase:
    """Use case for listing templates with pagination."""

    def __init__(self, template_repository: TemplateRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            template_repository: Template repository
        """
        self._template_repository = template_repository

    async def execute(
        self,
        organization_id: str,
        page: int = 1,
        limit: int = 20,
        include_defaults: bool = True,
    ) -> TemplateListResponse:
        """Execute list templates.

        Args:
            organization_id: Organization ID
            page: Page number (1-based)
            limit: Number of templates per page
            include_defaults: Whether to include default templates

        Returns:
            Template list response DTO with pagination metadata
        """
        org_uuid = UUID(organization_id)
        offset = (page - 1) * limit

        logger.info(
            "Listing templates",
            organization_id=organization_id,
            page=page,
            limit=limit,
            include_defaults=include_defaults,
        )

        templates = await self._template_repository.get_all(
            organization_id=org_uuid, skip=offset, limit=limit, include_defaults=include_defaults
        )
        total = await self._template_repository.count(
            organization_id=org_uuid, include_defaults=include_defaults
        )

        # Calculate total pages
        pages = ceil(total / limit) if total > 0 else 0

        template_responses = [
            TemplateListItemResponse(
                id=t.id,
                organization_id=t.organization_id,
                name=t.name,
                description=t.description,
                is_default=t.is_default,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in templates
        ]

        logger.info("Templates listed", count=len(template_responses), total=total, pages=pages)

        return TemplateListResponse(
            templates=template_responses,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )
