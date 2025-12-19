"""Whiteboard management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from src.application.dtos.whiteboard import (
    CreateWhiteboardRequest,
    UpdateWhiteboardRequest,
    WhiteboardResponse,
)
from src.application.use_cases.whiteboard import (
    CreateWhiteboardUseCase,
    DeleteWhiteboardUseCase,
    GetWhiteboardUseCase,
    UpdateWhiteboardUseCase,
)
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import SpaceRepository, WhiteboardRepository
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_organization_member
from src.presentation.dependencies.services import (
    get_permission_service,
    get_space_repository,
    get_whiteboard_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_create_whiteboard_use_case(
    whiteboard_repository: Annotated[WhiteboardRepository, Depends(get_whiteboard_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
) -> CreateWhiteboardUseCase:
    """Get create whiteboard use case with dependencies."""
    return CreateWhiteboardUseCase(whiteboard_repository, space_repository)


def get_get_whiteboard_use_case(
    whiteboard_repository: Annotated[WhiteboardRepository, Depends(get_whiteboard_repository)],
) -> GetWhiteboardUseCase:
    """Get whiteboard use case with dependencies."""
    return GetWhiteboardUseCase(whiteboard_repository)


def get_update_whiteboard_use_case(
    whiteboard_repository: Annotated[WhiteboardRepository, Depends(get_whiteboard_repository)],
) -> UpdateWhiteboardUseCase:
    """Get update whiteboard use case with dependencies."""
    return UpdateWhiteboardUseCase(whiteboard_repository)


def get_delete_whiteboard_use_case(
    whiteboard_repository: Annotated[WhiteboardRepository, Depends(get_whiteboard_repository)],
) -> DeleteWhiteboardUseCase:
    """Get delete whiteboard use case with dependencies."""
    return DeleteWhiteboardUseCase(whiteboard_repository)


@router.post("/", response_model=WhiteboardResponse, status_code=status.HTTP_201_CREATED)
async def create_whiteboard(
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: CreateWhiteboardRequest,
    use_case: Annotated[CreateWhiteboardUseCase, Depends(get_create_whiteboard_use_case)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> WhiteboardResponse:
    """Create a new whiteboard.

    Requires space membership (via organization membership).

    Args:
        current_user: Current authenticated user
        request: Create whiteboard request
        use_case: Create whiteboard use case
        space_repository: Space repository
        permission_service: Permission service

    Returns:
        Created whiteboard response

    Raises:
        HTTPException: If space not found or user lacks permission
    """
    # Check user has edit permissions
    space = await space_repository.get_by_id(request.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(request.space_id))

    await require_organization_member(space.organization_id, current_user, permission_service)

    return await use_case.execute(request, str(current_user.id))


@router.get("/{whiteboard_id}", response_model=WhiteboardResponse, status_code=status.HTTP_200_OK)
async def get_whiteboard(
    current_user: Annotated[User, Depends(get_current_active_user)],
    whiteboard_id: UUID,
    use_case: Annotated[GetWhiteboardUseCase, Depends(get_get_whiteboard_use_case)],
    whiteboard_repository: Annotated[WhiteboardRepository, Depends(get_whiteboard_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> WhiteboardResponse:
    """Get whiteboard by ID.

    Requires space membership (via organization membership).

    Args:
        current_user: Current authenticated user
        whiteboard_id: Whiteboard UUID (from path)
        use_case: Get whiteboard use case
        whiteboard_repository: Whiteboard repository
        space_repository: Space repository
        permission_service: Permission service

    Returns:
        Whiteboard response

    Raises:
        HTTPException: If whiteboard not found or user lacks permission
    """
    whiteboard = await whiteboard_repository.get_by_id(whiteboard_id)
    if whiteboard is None:
        raise EntityNotFoundException("Whiteboard", str(whiteboard_id))

    space = await space_repository.get_by_id(whiteboard.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(whiteboard.space_id))

    await require_organization_member(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(whiteboard_id))


@router.put("/{whiteboard_id}", response_model=WhiteboardResponse, status_code=status.HTTP_200_OK)
async def update_whiteboard(
    current_user: Annotated[User, Depends(get_current_active_user)],
    whiteboard_id: UUID,
    request: UpdateWhiteboardRequest,
    use_case: Annotated[UpdateWhiteboardUseCase, Depends(get_update_whiteboard_use_case)],
    whiteboard_repository: Annotated[WhiteboardRepository, Depends(get_whiteboard_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> WhiteboardResponse:
    """Update a whiteboard.

    Requires space membership (via organization membership).

    Args:
        current_user: Current authenticated user
        whiteboard_id: Whiteboard UUID (from path)
        request: Update whiteboard request
        use_case: Update whiteboard use case
        whiteboard_repository: Whiteboard repository
        space_repository: Space repository
        permission_service: Permission service

    Returns:
        Updated whiteboard response

    Raises:
        HTTPException: If whiteboard not found or user lacks permission
    """
    whiteboard = await whiteboard_repository.get_by_id(whiteboard_id)
    if whiteboard is None:
        raise EntityNotFoundException("Whiteboard", str(whiteboard_id))

    space = await space_repository.get_by_id(whiteboard.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(whiteboard.space_id))

    await require_organization_member(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(whiteboard_id), request, str(current_user.id))


@router.delete("/{whiteboard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_whiteboard(
    current_user: Annotated[User, Depends(get_current_active_user)],
    whiteboard_id: UUID,
    use_case: Annotated[DeleteWhiteboardUseCase, Depends(get_delete_whiteboard_use_case)],
    whiteboard_repository: Annotated[WhiteboardRepository, Depends(get_whiteboard_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete a whiteboard.

    Requires space membership (via organization membership).

    Args:
        current_user: Current authenticated user
        whiteboard_id: Whiteboard UUID (from path)
        use_case: Delete whiteboard use case
        whiteboard_repository: Whiteboard repository
        space_repository: Space repository
        permission_service: Permission service

    Raises:
        HTTPException: If whiteboard not found or user lacks permission
    """
    whiteboard = await whiteboard_repository.get_by_id(whiteboard_id)
    if whiteboard is None:
        raise EntityNotFoundException("Whiteboard", str(whiteboard_id))

    space = await space_repository.get_by_id(whiteboard.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(whiteboard.space_id))

    await require_organization_member(space.organization_id, current_user, permission_service)

    await use_case.execute(str(whiteboard_id))


@router.get("/{whiteboard_id}/export", status_code=status.HTTP_200_OK)
async def export_whiteboard(
    current_user: Annotated[User, Depends(get_current_active_user)],
    whiteboard_id: UUID,
    whiteboard_repository: Annotated[WhiteboardRepository, Depends(get_whiteboard_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    format: str = Query("json", description="Export format (json, png)"),
) -> Response:
    """Export whiteboard to image or JSON.

    Requires space membership (via organization membership).

    Args:
        current_user: Current authenticated user
        whiteboard_id: Whiteboard UUID (from path)
        whiteboard_repository: Whiteboard repository
        space_repository: Space repository
        permission_service: Permission service
        format: Export format (json, png)

    Returns:
        File response with exported content

    Raises:
        HTTPException: If whiteboard not found, format invalid, or user lacks permission
    """
    whiteboard = await whiteboard_repository.get_by_id(whiteboard_id)
    if whiteboard is None:
        raise EntityNotFoundException("Whiteboard", str(whiteboard_id))

    space = await space_repository.get_by_id(whiteboard.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(whiteboard.space_id))

    await require_organization_member(space.organization_id, current_user, permission_service)

    # Export based on format
    if format.lower() == "json":
        import json

        content = json.dumps({"name": whiteboard.name, "data": whiteboard.data}, indent=2)
        return Response(
            content=content.encode("utf-8"),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{whiteboard.name}.json"'},
        )
    elif format.lower() == "png":
        # For PNG export, we'd need a library to render the whiteboard
        # For now, return a placeholder
        return Response(
            content=b"PNG export not yet implemented",
            media_type="image/png",
            headers={"Content-Disposition": f'attachment; filename="{whiteboard.name}.png"'},
        )
    else:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid export format: {format}. Must be 'json' or 'png'",
        )
