"""Template management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.application.dtos.template import (
    CreateTemplateRequest,
    TemplateListResponse,
    TemplateResponse,
    UpdateTemplateRequest,
)
from src.application.use_cases.template import (
    CreateTemplateUseCase,
    DeleteTemplateUseCase,
    GetTemplateUseCase,
    ListTemplatesUseCase,
    UpdateTemplateUseCase,
)
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    OrganizationRepository,
    TemplateRepository,
    UserRepository,
)
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import (
    require_edit_permission,
    require_organization_admin,
    require_organization_member,
)
from src.presentation.dependencies.services import (
    get_organization_repository,
    get_permission_service,
    get_template_repository,
    get_user_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_create_template_use_case(
    template_repository: Annotated[TemplateRepository, Depends(get_template_repository)],
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> CreateTemplateUseCase:
    """Get create template use case with dependencies."""
    return CreateTemplateUseCase(template_repository, organization_repository, user_repository)


def get_template_use_case(
    template_repository: Annotated[TemplateRepository, Depends(get_template_repository)],
) -> GetTemplateUseCase:
    """Get template use case with dependencies."""
    return GetTemplateUseCase(template_repository)


def get_list_templates_use_case(
    template_repository: Annotated[TemplateRepository, Depends(get_template_repository)],
) -> ListTemplatesUseCase:
    """Get list templates use case with dependencies."""
    return ListTemplatesUseCase(template_repository)


def get_update_template_use_case(
    template_repository: Annotated[TemplateRepository, Depends(get_template_repository)],
) -> UpdateTemplateUseCase:
    """Get update template use case with dependencies."""
    return UpdateTemplateUseCase(template_repository)


def get_delete_template_use_case(
    template_repository: Annotated[TemplateRepository, Depends(get_template_repository)],
) -> DeleteTemplateUseCase:
    """Get delete template use case with dependencies."""
    return DeleteTemplateUseCase(template_repository)


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: CreateTemplateRequest,
    use_case: Annotated[CreateTemplateUseCase, Depends(get_create_template_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> TemplateResponse:
    """Create a new template.

    Requires organization membership.
    """
    # Check user has edit permissions
    await require_edit_permission(request.organization_id, current_user, permission_service)

    return await use_case.execute(request, str(current_user.id))


@router.get("/{template_id}", response_model=TemplateResponse, status_code=status.HTTP_200_OK)
async def get_template(
    current_user: Annotated[User, Depends(get_current_active_user)],
    template_id: UUID,
    use_case: Annotated[GetTemplateUseCase, Depends(get_template_use_case)],
    template_repository: Annotated[TemplateRepository, Depends(get_template_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> TemplateResponse:
    """Get template by ID.

    Requires organization membership.
    """
    template = await template_repository.get_by_id(template_id)

    if template is None:
        raise EntityNotFoundException("Template", str(template_id))

    # Check user is member of the organization
    await require_organization_member(template.organization_id, current_user, permission_service)

    return await use_case.execute(str(template_id))


@router.get("/", response_model=TemplateListResponse, status_code=status.HTTP_200_OK)
async def list_templates(
    current_user: Annotated[User, Depends(get_current_active_user)],
    organization_id: Annotated[UUID, Query(..., description="Organization ID")],
    use_case: Annotated[ListTemplatesUseCase, Depends(get_list_templates_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of templates per page")] = 20,
    include_defaults: Annotated[
        bool, Query(description="Whether to include default templates")
    ] = True,
) -> TemplateListResponse:
    """List templates in an organization.

    Requires organization membership.
    """
    # Check user is member of the organization
    await require_organization_member(organization_id, current_user, permission_service)

    return await use_case.execute(
        str(organization_id),
        page=page,
        limit=limit,
        include_defaults=include_defaults,
    )


@router.put("/{template_id}", response_model=TemplateResponse, status_code=status.HTTP_200_OK)
async def update_template(
    current_user: Annotated[User, Depends(get_current_active_user)],
    template_id: UUID,
    request: UpdateTemplateRequest,
    use_case: Annotated[UpdateTemplateUseCase, Depends(get_update_template_use_case)],
    template_repository: Annotated[TemplateRepository, Depends(get_template_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> TemplateResponse:
    """Update a template.

    Requires organization admin role.
    """
    template = await template_repository.get_by_id(template_id)

    if template is None:
        raise EntityNotFoundException("Template", str(template_id))

    # Check user is admin of the organization
    await require_organization_admin(template.organization_id, current_user, permission_service)

    return await use_case.execute(str(template_id), request)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    current_user: Annotated[User, Depends(get_current_active_user)],
    template_id: UUID,
    use_case: Annotated[DeleteTemplateUseCase, Depends(get_delete_template_use_case)],
    template_repository: Annotated[TemplateRepository, Depends(get_template_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete a template (soft delete).

    Requires organization admin role.
    """
    template = await template_repository.get_by_id(template_id)

    if template is None:
        raise EntityNotFoundException("Template", str(template_id))

    # Check user is admin of the organization
    await require_organization_admin(template.organization_id, current_user, permission_service)

    await use_case.execute(str(template_id))
