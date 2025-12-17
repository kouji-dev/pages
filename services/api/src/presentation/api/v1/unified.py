"""Unified folders and nodes API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.application.dtos.unified import UnifiedListResponse
from src.application.use_cases.unified import ListFoldersAndNodesUseCase
from src.domain.entities import User
from src.domain.repositories import FolderRepository, ProjectRepository, SpaceRepository
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_organization_member
from src.presentation.dependencies.services import (
    get_folder_repository,
    get_permission_service,
    get_project_repository,
    get_space_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_list_folders_and_nodes_use_case(
    folder_repository: Annotated[FolderRepository, Depends(get_folder_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
) -> ListFoldersAndNodesUseCase:
    """Get list folders and nodes use case with dependencies."""
    return ListFoldersAndNodesUseCase(folder_repository, project_repository, space_repository)


@router.get(
    "/organizations/{organization_id}/items",
    response_model=UnifiedListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_folders_and_nodes(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListFoldersAndNodesUseCase, Depends(get_list_folders_and_nodes_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    folder_id: UUID | None = Query(None, description="Filter nodes by folder ID"),
    parent_id: UUID | None = Query(None, description="Filter folders by parent ID"),
    include_empty_folders: bool = Query(True, description="Include folders with no nodes"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
) -> UnifiedListResponse:
    """List folders and nodes (projects + spaces) in an organization.

    Returns a unified list of folders and nodes with their details.

    Args:
        organization_id: Organization UUID (from path)
        current_user: Current authenticated user
        use_case: List folders and nodes use case
        permission_service: Permission service
        folder_id: Optional folder ID to filter nodes by
        parent_id: Optional parent folder ID to filter folders by
        include_empty_folders: Whether to include folders with no nodes
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Unified list response with folders and nodes

    Raises:
        HTTPException: If user is not a member of the organization
    """
    # Verify user is a member
    await require_organization_member(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    return await use_case.execute(
        organization_id=str(organization_id),
        folder_id=str(folder_id) if folder_id else None,
        parent_id=str(parent_id) if parent_id else None,
        include_empty_folders=include_empty_folders,
        skip=skip,
        limit=limit,
    )
