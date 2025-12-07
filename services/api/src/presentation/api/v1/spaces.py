"""Space management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.space import (
    CreateSpaceRequest,
    SpaceListResponse,
    SpaceResponse,
    UpdateSpaceRequest,
)
from src.application.use_cases.space import (
    CreateSpaceUseCase,
    DeleteSpaceUseCase,
    GetSpaceUseCase,
    ListSpacesUseCase,
    UpdateSpaceUseCase,
)
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    OrganizationRepository,
    SpaceRepository,
    UserRepository,
)
from src.domain.services import PermissionService
from src.infrastructure.database import get_session
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import (
    require_organization_admin,
    require_organization_member,
)
from src.presentation.dependencies.services import (
    get_organization_repository,
    get_permission_service,
    get_space_repository,
    get_user_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_create_space_use_case(
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateSpaceUseCase:
    """Get create space use case with dependencies."""
    return CreateSpaceUseCase(space_repository, organization_repository, user_repository, session)


def get_space_use_case(
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetSpaceUseCase:
    """Get space use case with dependencies."""
    return GetSpaceUseCase(space_repository, session)


def get_list_spaces_use_case(
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListSpacesUseCase:
    """Get list spaces use case with dependencies."""
    return ListSpacesUseCase(space_repository, session)


def get_update_space_use_case(
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UpdateSpaceUseCase:
    """Get update space use case with dependencies."""
    return UpdateSpaceUseCase(space_repository, session)


def get_delete_space_use_case(
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
) -> DeleteSpaceUseCase:
    """Get delete space use case with dependencies."""
    return DeleteSpaceUseCase(space_repository)


@router.post("/", response_model=SpaceResponse, status_code=status.HTTP_201_CREATED)
async def create_space(
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: CreateSpaceRequest,
    use_case: Annotated[CreateSpaceUseCase, Depends(get_create_space_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> SpaceResponse:
    """Create a new space.

    Requires organization membership.
    """
    # Check user is member of the organization
    await require_organization_member(request.organization_id, current_user, permission_service)

    return await use_case.execute(request, str(current_user.id))


@router.get("/{space_id}", response_model=SpaceResponse, status_code=status.HTTP_200_OK)
async def get_space(
    current_user: Annotated[User, Depends(get_current_active_user)],
    space_id: UUID,
    use_case: Annotated[GetSpaceUseCase, Depends(get_space_use_case)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> SpaceResponse:
    """Get space by ID.

    Requires space membership (via organization membership).
    """
    space = await space_repository.get_by_id(space_id)

    if space is None:
        raise EntityNotFoundException("Space", str(space_id))

    # Check user is member of the organization
    await require_organization_member(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(space_id))


@router.get("/", response_model=SpaceListResponse, status_code=status.HTTP_200_OK)
async def list_spaces(
    current_user: Annotated[User, Depends(get_current_active_user)],
    organization_id: Annotated[UUID, Query(..., description="Organization ID")],
    use_case: Annotated[ListSpacesUseCase, Depends(get_list_spaces_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of spaces per page")] = 20,
    search: Annotated[str | None, Query(description="Search query (name or key)")] = None,
) -> SpaceListResponse:
    """List spaces in an organization.

    Requires organization membership.
    """
    # Check user is member of the organization
    await require_organization_member(organization_id, current_user, permission_service)

    return await use_case.execute(
        str(organization_id),
        page=page,
        limit=limit,
        search=search,
    )


@router.put("/{space_id}", response_model=SpaceResponse, status_code=status.HTTP_200_OK)
async def update_space(
    current_user: Annotated[User, Depends(get_current_active_user)],
    space_id: UUID,
    request: UpdateSpaceRequest,
    use_case: Annotated[UpdateSpaceUseCase, Depends(get_update_space_use_case)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> SpaceResponse:
    """Update a space.

    Requires space admin role (organization admin).
    """
    space = await space_repository.get_by_id(space_id)

    if space is None:
        raise EntityNotFoundException("Space", str(space_id))

    # Check user is admin of the organization
    await require_organization_admin(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(space_id), request)


@router.delete("/{space_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_space(
    current_user: Annotated[User, Depends(get_current_active_user)],
    space_id: UUID,
    use_case: Annotated[DeleteSpaceUseCase, Depends(get_delete_space_use_case)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete a space (soft delete).

    Requires organization admin role.
    """
    space = await space_repository.get_by_id(space_id)

    if space is None:
        raise EntityNotFoundException("Space", str(space_id))

    # Check user is admin of the organization
    await require_organization_admin(space.organization_id, current_user, permission_service)

    await use_case.execute(str(space_id))
