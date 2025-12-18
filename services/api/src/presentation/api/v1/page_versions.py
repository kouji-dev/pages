"""Page version management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.application.dtos.page_version import (
    PageVersionDiffResponse,
    PageVersionListResponse,
    PageVersionResponse,
    RestorePageVersionResponse,
)
from src.application.use_cases.page_version import (
    GetPageVersionDiffUseCase,
    GetPageVersionUseCase,
    ListPageVersionsUseCase,
    RestorePageVersionUseCase,
)
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageRepository, PageVersionRepository, SpaceRepository
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import (
    require_edit_permission,
    require_organization_member,
)
from src.presentation.dependencies.services import (
    get_page_repository,
    get_page_version_repository,
    get_permission_service,
    get_space_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_list_page_versions_use_case(
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    page_version_repository: Annotated[PageVersionRepository, Depends(get_page_version_repository)],
) -> ListPageVersionsUseCase:
    """Get list page versions use case with dependencies."""
    return ListPageVersionsUseCase(page_repository, page_version_repository)


def get_get_page_version_use_case(
    page_version_repository: Annotated[PageVersionRepository, Depends(get_page_version_repository)],
) -> GetPageVersionUseCase:
    """Get page version use case with dependencies."""
    return GetPageVersionUseCase(page_version_repository)


def get_restore_page_version_use_case(
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    page_version_repository: Annotated[PageVersionRepository, Depends(get_page_version_repository)],
) -> RestorePageVersionUseCase:
    """Get restore page version use case with dependencies."""
    return RestorePageVersionUseCase(page_repository, page_version_repository)


def get_get_page_version_diff_use_case(
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    page_version_repository: Annotated[PageVersionRepository, Depends(get_page_version_repository)],
) -> GetPageVersionDiffUseCase:
    """Get page version diff use case with dependencies."""
    return GetPageVersionDiffUseCase(page_repository, page_version_repository)


@router.get(
    "/pages/{page_id}/versions",
    response_model=PageVersionListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_page_versions(
    page_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListPageVersionsUseCase, Depends(get_list_page_versions_use_case)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Number of versions per page"),
) -> PageVersionListResponse:
    """List page versions.

    Returns a paginated list of versions for a page.

    Args:
        page_id: Page UUID (from path)
        current_user: Current authenticated user
        use_case: List page versions use case
        page_repository: Page repository
        space_repository: Space repository
        permission_service: Permission service
        page: Page number (1-based)
        limit: Number of versions per page

    Returns:
        Page version list response with pagination metadata

    Raises:
        HTTPException: If page not found or user lacks permission
    """
    # Verify user has read permission on the page
    page_entity = await page_repository.get_by_id(page_id)
    if page_entity is None:
        from src.domain.exceptions import EntityNotFoundException

        raise EntityNotFoundException("Page", str(page_id))

    space = await space_repository.get_by_id(page_entity.space_id)
    if space is None:
        from src.domain.exceptions import EntityNotFoundException

        raise EntityNotFoundException("Space", str(page_entity.space_id))

    await require_organization_member(space.organization_id, current_user, permission_service)

    return await use_case.execute(
        page_id=str(page_id),
        page=page,
        limit=limit,
    )


@router.get(
    "/page-versions/{version_id}",
    response_model=PageVersionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_page_version(
    version_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetPageVersionUseCase, Depends(get_get_page_version_use_case)],
) -> PageVersionResponse:
    """Get a page version by ID.

    Returns the full content of a specific page version.

    Args:
        version_id: Page version UUID (from path)
        current_user: Current authenticated user
        use_case: Get page version use case

    Returns:
        Page version response

    Raises:
        HTTPException: If version not found
    """
    return await use_case.execute(str(version_id))


@router.post(
    "/page-versions/{version_id}/restore",
    response_model=RestorePageVersionResponse,
    status_code=status.HTTP_200_OK,
)
async def restore_page_version(
    version_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[RestorePageVersionUseCase, Depends(get_restore_page_version_use_case)],
    page_version_repository: Annotated[PageVersionRepository, Depends(get_page_version_repository)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> RestorePageVersionResponse:
    """Restore a page from a version.

    Creates a new version from the restored content.

    Args:
        version_id: Page version UUID to restore (from path)
        current_user: Current authenticated user
        use_case: Restore page version use case
        page_version_repository: Page version repository
        page_repository: Page repository
        space_repository: Space repository
        permission_service: Permission service

    Returns:
        Restore page version response

    Raises:
        HTTPException: If version or page not found, or user lacks permission
    """
    # Get version to check page permissions
    version = await page_version_repository.get_by_id(version_id)
    if version is None:
        raise EntityNotFoundException("PageVersion", str(version_id))

    # Check edit permission on the page
    page = await page_repository.get_by_id(version.page_id)
    if page is None:
        raise EntityNotFoundException("Page", str(version.page_id))

    space = await space_repository.get_by_id(page.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(page.space_id))

    await require_edit_permission(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(version_id), restored_by=str(current_user.id))


@router.get(
    "/page-versions/{version_id}/diff",
    response_model=PageVersionDiffResponse,
    status_code=status.HTTP_200_OK,
)
async def get_page_version_diff(
    version_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetPageVersionDiffUseCase, Depends(get_get_page_version_diff_use_case)],
    compare_to_version_id: UUID | None = Query(
        None, description="Optional version ID to compare with (defaults to current page)"
    ),
) -> PageVersionDiffResponse:
    """Get diff between page versions.

    Returns the differences between a version and another version or the current page.

    Args:
        version_id: Page version UUID (from path)
        current_user: Current authenticated user
        use_case: Get page version diff use case
        compare_to_version_id: Optional version ID to compare with

    Returns:
        Page version diff response

    Raises:
        HTTPException: If version not found
    """
    return await use_case.execute(
        version_id=str(version_id),
        compare_to_version_id=str(compare_to_version_id) if compare_to_version_id else None,
    )
