"""Export API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from src.application.use_cases.export import ExportPageUseCase, ExportSpaceUseCase
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageRepository, SpaceRepository
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_organization_member
from src.presentation.dependencies.services import (
    get_page_repository,
    get_permission_service,
    get_space_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_export_page_use_case(
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
) -> ExportPageUseCase:
    """Get export page use case with dependencies."""
    return ExportPageUseCase(page_repository)


def get_export_space_use_case(
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
) -> ExportSpaceUseCase:
    """Get export space use case with dependencies."""
    return ExportSpaceUseCase(space_repository, page_repository)


@router.get("/pages/{page_id}/export/{format}")
async def export_page(
    page_id: UUID,
    format: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ExportPageUseCase, Depends(get_export_page_use_case)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> Response:
    """Export a page to PDF, Markdown, or HTML.

    Args:
        page_id: Page UUID (from path)
        format: Export format (pdf, markdown, html)
        current_user: Current authenticated user
        use_case: Export page use case
        page_repository: Page repository
        space_repository: Space repository
        permission_service: Permission service

    Returns:
        File response with exported content

    Raises:
        HTTPException: If page not found, format invalid, or user lacks permission
    """
    # Verify user has read permission on the page
    page = await page_repository.get_by_id(page_id)
    if page is None:
        raise EntityNotFoundException("Page", str(page_id))

    space = await space_repository.get_by_id(page.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(page.space_id))

    await require_organization_member(space.organization_id, current_user, permission_service)

    # Export page
    try:
        file_content, mime_type, filename = await use_case.execute(str(page_id), format)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return Response(
        content=file_content,
        media_type=mime_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/spaces/{space_id}/export")
async def export_space(
    space_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ExportSpaceUseCase, Depends(get_export_space_use_case)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    format: str = Query("html", description="Export format (html, markdown, pdf)"),
) -> Response:
    """Export a space (all pages) to HTML, Markdown, or PDF.

    Args:
        space_id: Space UUID (from path)
        current_user: Current authenticated user
        use_case: Export space use case
        space_repository: Space repository
        permission_service: Permission service
        format: Export format (html, markdown, pdf)

    Returns:
        File response with exported content

    Raises:
        HTTPException: If space not found, format invalid, or user lacks permission
    """
    # Verify user has read permission on the space
    space = await space_repository.get_by_id(space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(space_id))

    await require_organization_member(space.organization_id, current_user, permission_service)

    # Export space
    try:
        file_content, mime_type, filename = await use_case.execute(str(space_id), format)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return Response(
        content=file_content,
        media_type=mime_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
