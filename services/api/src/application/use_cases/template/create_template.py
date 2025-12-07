"""Create template use case."""

from uuid import UUID

import structlog

from src.application.dtos.template import CreateTemplateRequest, TemplateResponse
from src.domain.entities import Template
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import OrganizationRepository, TemplateRepository, UserRepository

logger = structlog.get_logger()


class CreateTemplateUseCase:
    """Use case for creating a template."""

    def __init__(
        self,
        template_repository: TemplateRepository,
        organization_repository: OrganizationRepository,
        user_repository: UserRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            template_repository: Template repository
            organization_repository: Organization repository to verify organization exists
            user_repository: User repository to verify creator exists
        """
        self._template_repository = template_repository
        self._organization_repository = organization_repository
        self._user_repository = user_repository

    async def execute(
        self, request: CreateTemplateRequest, creator_user_id: str
    ) -> TemplateResponse:
        """Execute template creation.

        Args:
            request: Template creation request
            creator_user_id: ID of the user creating the template

        Returns:
            Created template response DTO

        Raises:
            EntityNotFoundException: If organization or creator user not found
        """
        logger.info(
            "Creating template",
            name=request.name,
            organization_id=str(request.organization_id),
            creator_user_id=creator_user_id,
        )

        # Verify organization exists
        organization = await self._organization_repository.get_by_id(request.organization_id)
        if organization is None:
            logger.warning(
                "Organization not found for template creation",
                organization_id=str(request.organization_id),
            )
            raise EntityNotFoundException("Organization", str(request.organization_id))

        # Verify creator exists
        creator_uuid = UUID(creator_user_id)
        creator = await self._user_repository.get_by_id(creator_uuid)
        if creator is None:
            logger.warning("Creator user not found", creator_user_id=creator_user_id)
            raise EntityNotFoundException("User", creator_user_id)

        # Create template entity
        template = Template.create(
            organization_id=request.organization_id,
            name=request.name,
            description=request.description,
            content=request.content,
            is_default=request.is_default,
            created_by=creator_uuid,
        )

        # Persist template
        created_template = await self._template_repository.create(template)

        logger.info(
            "Template created successfully",
            template_id=str(created_template.id),
            name=created_template.name,
        )

        return TemplateResponse(
            id=created_template.id,
            organization_id=created_template.organization_id,
            name=created_template.name,
            description=created_template.description,
            content=created_template.content,
            is_default=created_template.is_default,
            created_by=created_template.created_by,
            created_at=created_template.created_at,
            updated_at=created_template.updated_at,
        )
