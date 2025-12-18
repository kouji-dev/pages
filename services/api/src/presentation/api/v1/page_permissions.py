"""Page and space permission management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.dtos.page_permission import (
    PagePermissionListResponse,
    SpacePermissionListResponse,
    UpdatePagePermissionRequest,
    UpdateSpacePermissionRequest,
)
from src.application.use_cases.page_permission import (
    GetPagePermissionsUseCase,
    GetSpacePermissionsUseCase,
    UpdatePagePermissionsUseCase,
    UpdateSpacePermissionsUseCase,
)
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    PagePermissionRepository,
    PageRepository,
    SpacePermissionRepository,
    SpaceRepository,
)
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_organization_admin
from src.presentation.dependencies.services import (
    get_page_permission_repository,
    get_page_repository,
    get_permission_service,
    get_space_permission_repository,
    get_space_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_get_page_permissions_use_case(
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    page_permission_repository: Annotated[
        PagePermissionRepository, Depends(get_page_permission_repository)
    ],
) -> GetPagePermissionsUseCase:
    """Get page permissions use case with dependencies."""
    return GetPagePermissionsUseCase(page_repository, page_permission_repository)


def get_update_page_permissions_use_case(
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    page_permission_repository: Annotated[
        PagePermissionRepository, Depends(get_page_permission_repository)
    ],
) -> UpdatePagePermissionsUseCase:
    """Update page permissions use case with dependencies."""
    return UpdatePagePermissionsUseCase(page_repository, page_permission_repository)


def get_get_space_permissions_use_case(
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    space_permission_repository: Annotated[
        SpacePermissionRepository, Depends(get_space_permission_repository)
    ],
) -> GetSpacePermissionsUseCase:
    """Get space permissions use case with dependencies."""
    return GetSpacePermissionsUseCase(space_repository, space_permission_repository)


def get_update_space_permissions_use_case(
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    space_permission_repository: Annotated[
        SpacePermissionRepository, Depends(get_space_permission_repository)
    ],
) -> UpdateSpacePermissionsUseCase:
    """Update space permissions use case with dependencies."""
    return UpdateSpacePermissionsUseCase(space_repository, space_permission_repository)


@router.get(
    "/pages/{page_id}/permissions",
    response_model=PagePermissionListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_page_permissions(
    page_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetPagePermissionsUseCase, Depends(get_get_page_permissions_use_case)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> PagePermissionListResponse:
    """Get page permissions.

    Requires organization admin or space admin.

    Args:
        page_id: Page UUID (from path)
        current_user: Current authenticated user
        use_case: Get page permissions use case
        page_repository: Page repository
        space_repository: Space repository
        permission_service: Permission service

    Returns:
        Page permission list response

    Raises:
        HTTPException: If page not found or user lacks permission
    """
    page = await page_repository.get_by_id(page_id)
    if page is None:
        raise EntityNotFoundException("Page", str(page_id))

    space = await space_repository.get_by_id(page.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(page.space_id))

    await require_organization_admin(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(page_id))


@router.put(
    "/pages/{page_id}/permissions",
    response_model=PagePermissionListResponse,
    status_code=status.HTTP_200_OK,
)
async def update_page_permissions(
    page_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: UpdatePagePermissionRequest,
    use_case: Annotated[
        UpdatePagePermissionsUseCase, Depends(get_update_page_permissions_use_case)
    ],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> PagePermissionListResponse:
    """Update page permissions.

    Requires organization admin or space admin.

    Args:
        page_id: Page UUID (from path)
        current_user: Current authenticated user
        request: Update page permission request
        use_case: Update page permissions use case
        page_repository: Page repository
        space_repository: Space repository
        permission_service: Permission service

    Returns:
        Updated page permission list response

    Raises:
        HTTPException: If page not found or user lacks permission
    """
    page = await page_repository.get_by_id(page_id)
    if page is None:
        raise EntityNotFoundException("Page", str(page_id))

    space = await space_repository.get_by_id(page.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(page.space_id))

    await require_organization_admin(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(page_id), request)


@router.get(
    "/spaces/{space_id}/permissions",
    response_model=SpacePermissionListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_space_permissions(
    space_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetSpacePermissionsUseCase, Depends(get_get_space_permissions_use_case)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> SpacePermissionListResponse:
    """Get space permissions.

    Requires organization admin.

    Args:
        space_id: Space UUID (from path)
        current_user: Current authenticated user
        use_case: Get space permissions use case
        space_repository: Space repository
        permission_service: Permission service

    Returns:
        Space permission list response

    Raises:
        HTTPException: If space not found or user lacks permission
    """
    space = await space_repository.get_by_id(space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(space_id))

    await require_organization_admin(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(space_id))


@router.put(
    "/spaces/{space_id}/permissions",
    response_model=SpacePermissionListResponse,
    status_code=status.HTTP_200_OK,
)
async def update_space_permissions(
    space_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: UpdateSpacePermissionRequest,
    use_case: Annotated[
        UpdateSpacePermissionsUseCase, Depends(get_update_space_permissions_use_case)
    ],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> SpacePermissionListResponse:
    """Update space permissions.

    Requires organization admin.

    Args:
        space_id: Space UUID (from path)
        current_user: Current authenticated user
        request: Update space permission request
        use_case: Update space permissions use case
        space_repository: Space repository
        permission_service: Permission service

    Returns:
        Updated space permission list response

    Raises:
        HTTPException: If space not found or user lacks permission
    """
    space = await space_repository.get_by_id(space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(space_id))

    await require_organization_admin(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(space_id), request)
