"""Page management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.page import (
    CreatePageRequest,
    PageListResponse,
    PageResponse,
    PageTreeResponse,
    UpdatePageRequest,
)
from src.application.use_cases.page import (
    CreatePageUseCase,
    DeletePageUseCase,
    GetPageTreeUseCase,
    GetPageUseCase,
    ListPagesUseCase,
    UpdatePageUseCase,
)
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    PageRepository,
    PageVersionRepository,
    SpaceRepository,
    UserRepository,
)
from src.domain.services import PermissionService
from src.infrastructure.database import get_session
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import (
    require_edit_permission,
    require_organization_admin,
    require_organization_member,
)
from src.presentation.dependencies.services import (
    get_page_repository,
    get_page_version_repository,
    get_permission_service,
    get_space_repository,
    get_user_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_create_page_use_case(
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreatePageUseCase:
    """Get create page use case with dependencies."""
    return CreatePageUseCase(page_repository, space_repository, user_repository, session)


def get_page_use_case(
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetPageUseCase:
    """Get page use case with dependencies."""
    return GetPageUseCase(page_repository, session)


def get_list_pages_use_case(
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListPagesUseCase:
    """Get list pages use case with dependencies."""
    return ListPagesUseCase(page_repository, session)


def get_update_page_use_case(
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    page_version_repository: Annotated[PageVersionRepository, Depends(get_page_version_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UpdatePageUseCase:
    """Get update page use case with dependencies."""
    return UpdatePageUseCase(page_repository, page_version_repository, session)


def get_delete_page_use_case(
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
) -> DeletePageUseCase:
    """Get delete page use case with dependencies."""
    return DeletePageUseCase(page_repository)


def get_page_tree_use_case(
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
) -> GetPageTreeUseCase:
    """Get page tree use case with dependencies."""
    return GetPageTreeUseCase(page_repository)


@router.post("/", response_model=PageResponse, status_code=status.HTTP_201_CREATED)
async def create_page(
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: CreatePageRequest,
    use_case: Annotated[CreatePageUseCase, Depends(get_create_page_use_case)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> PageResponse:
    """Create a new page.

    Requires space membership (via organization membership).
    """
    # Check user has edit permissions
    space = await space_repository.get_by_id(request.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(request.space_id))

    await require_edit_permission(space.organization_id, current_user, permission_service)

    return await use_case.execute(request, str(current_user.id))


@router.get("/{page_id}", response_model=PageResponse, status_code=status.HTTP_200_OK)
async def get_page(
    current_user: Annotated[User, Depends(get_current_active_user)],
    page_id: UUID,
    use_case: Annotated[GetPageUseCase, Depends(get_page_use_case)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> PageResponse:
    """Get page by ID.

    Requires space membership (via organization membership).
    """
    page = await page_repository.get_by_id(page_id)

    if page is None:
        raise EntityNotFoundException("Page", str(page_id))

    # Check user is member of the organization
    space = await space_repository.get_by_id(page.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(page.space_id))

    await require_organization_member(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(page_id))


@router.get("/", response_model=PageListResponse, status_code=status.HTTP_200_OK)
async def list_pages(
    current_user: Annotated[User, Depends(get_current_active_user)],
    space_id: Annotated[UUID, Query(..., description="Space ID")],
    use_case: Annotated[ListPagesUseCase, Depends(get_list_pages_use_case)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of pages per page")] = 20,
    search: Annotated[str | None, Query(description="Search query (title or content)")] = None,
    parent_id: Annotated[
        UUID | None, Query(description="Parent page ID to filter by (None for root pages)")
    ] = None,
) -> PageListResponse:
    """List pages in a space.

    Requires space membership (via organization membership).
    """
    # Check user is member of the organization
    space = await space_repository.get_by_id(space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(space_id))

    await require_organization_member(space.organization_id, current_user, permission_service)

    return await use_case.execute(
        str(space_id),
        page=page,
        limit=limit,
        search=search,
        parent_id=str(parent_id) if parent_id else None,
    )


@router.put("/{page_id}", response_model=PageResponse, status_code=status.HTTP_200_OK)
async def update_page(
    current_user: Annotated[User, Depends(get_current_active_user)],
    page_id: UUID,
    request: UpdatePageRequest,
    use_case: Annotated[UpdatePageUseCase, Depends(get_update_page_use_case)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> PageResponse:
    """Update a page.

    Requires space membership (via organization membership).
    """
    page = await page_repository.get_by_id(page_id)

    if page is None:
        raise EntityNotFoundException("Page", str(page_id))

    # Check user has edit permissions
    space = await space_repository.get_by_id(page.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(page.space_id))

    await require_edit_permission(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(page_id), request, str(current_user.id))


@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page(
    current_user: Annotated[User, Depends(get_current_active_user)],
    page_id: UUID,
    use_case: Annotated[DeletePageUseCase, Depends(get_delete_page_use_case)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete a page (soft delete).

    Requires page author or space admin (organization admin).
    """
    page = await page_repository.get_by_id(page_id)

    if page is None:
        raise EntityNotFoundException("Page", str(page_id))

    # Check user is author or admin of the organization
    space = await space_repository.get_by_id(page.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(page.space_id))

    is_author = page.created_by == current_user.id
    if not is_author:
        await require_organization_admin(space.organization_id, current_user, permission_service)

    await use_case.execute(str(page_id))


@router.get(
    "/spaces/{space_id}/tree",
    response_model=PageTreeResponse,
    status_code=status.HTTP_200_OK,
)
async def get_page_tree(
    current_user: Annotated[User, Depends(get_current_active_user)],
    space_id: UUID,
    use_case: Annotated[GetPageTreeUseCase, Depends(get_page_tree_use_case)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> PageTreeResponse:
    """Get page tree structure for a space.

    Requires space membership (via organization membership).
    """
    space = await space_repository.get_by_id(space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(space_id))

    await require_organization_member(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(space_id))
