"""Saved filter management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.dtos.saved_filter import (
    CreateSavedFilterRequest,
    SavedFilterListResponse,
    SavedFilterResponse,
    UpdateSavedFilterRequest,
)
from src.application.use_cases.saved_filter import (
    CreateSavedFilterUseCase,
    DeleteSavedFilterUseCase,
    GetSavedFilterUseCase,
    ListSavedFiltersUseCase,
    UpdateSavedFilterUseCase,
)
from src.domain.entities import User
from src.domain.repositories import ProjectRepository
from src.domain.repositories.saved_filter_repository import SavedFilterRepository
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_edit_permission
from src.presentation.dependencies.services import (
    get_permission_service,
    get_project_repository,
    get_saved_filter_repository,
)

router = APIRouter(tags=["Saved Filters"])


def get_create_saved_filter_use_case(
    saved_filter_repository: Annotated[SavedFilterRepository, Depends(get_saved_filter_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> CreateSavedFilterUseCase:
    """Get create saved filter use case."""
    return CreateSavedFilterUseCase(saved_filter_repository, project_repository)


def get_get_saved_filter_use_case(
    saved_filter_repository: Annotated[SavedFilterRepository, Depends(get_saved_filter_repository)],
) -> GetSavedFilterUseCase:
    """Get saved filter use case."""
    return GetSavedFilterUseCase(saved_filter_repository)


def get_list_saved_filters_use_case(
    saved_filter_repository: Annotated[SavedFilterRepository, Depends(get_saved_filter_repository)],
) -> ListSavedFiltersUseCase:
    """Get list saved filters use case."""
    return ListSavedFiltersUseCase(saved_filter_repository)


def get_update_saved_filter_use_case(
    saved_filter_repository: Annotated[SavedFilterRepository, Depends(get_saved_filter_repository)],
) -> UpdateSavedFilterUseCase:
    """Get update saved filter use case."""
    return UpdateSavedFilterUseCase(saved_filter_repository)


def get_delete_saved_filter_use_case(
    saved_filter_repository: Annotated[SavedFilterRepository, Depends(get_saved_filter_repository)],
) -> DeleteSavedFilterUseCase:
    """Get delete saved filter use case."""
    return DeleteSavedFilterUseCase(saved_filter_repository)


@router.post(
    "/saved-filters",
    response_model=SavedFilterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create saved filter",
)
async def create_saved_filter(
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: CreateSavedFilterRequest,
    use_case: Annotated[CreateSavedFilterUseCase, Depends(get_create_saved_filter_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> SavedFilterResponse:
    """Create a new saved filter."""
    if request.project_id:
        project = await project_repository.get_by_id(request.project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        await require_edit_permission(
            project.organization_id,
            current_user,
            permission_service,
            project_id=project.id,
        )

    try:
        return await use_case.execute(current_user.id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/saved-filters/{filter_id}",
    response_model=SavedFilterResponse,
    status_code=status.HTTP_200_OK,
    summary="Get saved filter",
)
async def get_saved_filter(
    current_user: Annotated[User, Depends(get_current_active_user)],
    filter_id: UUID,
    use_case: Annotated[GetSavedFilterUseCase, Depends(get_get_saved_filter_use_case)],
    saved_filter_repository: Annotated[SavedFilterRepository, Depends(get_saved_filter_repository)],
) -> SavedFilterResponse:
    """Get saved filter by ID."""
    saved_filter = await saved_filter_repository.get_by_id(filter_id)
    if saved_filter is None:
        raise HTTPException(status_code=404, detail="Saved filter not found")

    # Check ownership
    if saved_filter.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return await use_case.execute(filter_id)


@router.get(
    "/saved-filters",
    response_model=SavedFilterListResponse,
    status_code=status.HTTP_200_OK,
    summary="List saved filters",
)
async def list_saved_filters(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListSavedFiltersUseCase, Depends(get_list_saved_filters_use_case)],
    project_id: Annotated[UUID | None, Query(description="Filter by project ID")] = None,
) -> SavedFilterListResponse:
    """List saved filters for current user."""
    return await use_case.execute(current_user.id, project_id)


@router.put(
    "/saved-filters/{filter_id}",
    response_model=SavedFilterResponse,
    status_code=status.HTTP_200_OK,
    summary="Update saved filter",
)
async def update_saved_filter(
    current_user: Annotated[User, Depends(get_current_active_user)],
    filter_id: UUID,
    request: UpdateSavedFilterRequest,
    use_case: Annotated[UpdateSavedFilterUseCase, Depends(get_update_saved_filter_use_case)],
    saved_filter_repository: Annotated[SavedFilterRepository, Depends(get_saved_filter_repository)],
) -> SavedFilterResponse:
    """Update a saved filter."""
    saved_filter = await saved_filter_repository.get_by_id(filter_id)
    if saved_filter is None:
        raise HTTPException(status_code=404, detail="Saved filter not found")

    # Check ownership
    if saved_filter.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        return await use_case.execute(filter_id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete(
    "/saved-filters/{filter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete saved filter",
)
async def delete_saved_filter(
    current_user: Annotated[User, Depends(get_current_active_user)],
    filter_id: UUID,
    use_case: Annotated[DeleteSavedFilterUseCase, Depends(get_delete_saved_filter_use_case)],
    saved_filter_repository: Annotated[SavedFilterRepository, Depends(get_saved_filter_repository)],
) -> None:
    """Delete a saved filter."""
    saved_filter = await saved_filter_repository.get_by_id(filter_id)
    if saved_filter is None:
        raise HTTPException(status_code=404, detail="Saved filter not found")

    # Check ownership
    if saved_filter.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    await use_case.execute(filter_id)
