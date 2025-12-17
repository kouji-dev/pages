"""Folder management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.folder import (
    AssignNodesToFolderRequest,
    CreateFolderRequest,
    FolderListResponse,
    FolderResponse,
    UpdateFolderRequest,
)
from src.application.use_cases.folder import (
    AssignNodesToFolderUseCase,
    CreateFolderUseCase,
    DeleteFolderUseCase,
    GetFolderUseCase,
    ListFoldersUseCase,
    UpdateFolderUseCase,
)
from src.domain.entities import User
from src.domain.repositories import (
    FolderRepository,
    OrganizationRepository,
    ProjectRepository,
    SpaceRepository,
)
from src.domain.services import PermissionService
from src.infrastructure.database import get_session
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import (
    require_organization_admin,
    require_organization_member,
)
from src.presentation.dependencies.services import (
    get_folder_repository,
    get_organization_repository,
    get_permission_service,
    get_project_repository,
    get_space_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_create_folder_use_case(
    folder_repository: Annotated[FolderRepository, Depends(get_folder_repository)],
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
) -> CreateFolderUseCase:
    """Get create folder use case with dependencies."""
    return CreateFolderUseCase(folder_repository, organization_repository)


def get_get_folder_use_case(
    folder_repository: Annotated[FolderRepository, Depends(get_folder_repository)],
) -> GetFolderUseCase:
    """Get folder use case with dependencies."""
    return GetFolderUseCase(folder_repository)


def get_list_folders_use_case(
    folder_repository: Annotated[FolderRepository, Depends(get_folder_repository)],
) -> ListFoldersUseCase:
    """Get list folders use case with dependencies."""
    return ListFoldersUseCase(folder_repository)


def get_update_folder_use_case(
    folder_repository: Annotated[FolderRepository, Depends(get_folder_repository)],
) -> UpdateFolderUseCase:
    """Get update folder use case with dependencies."""
    return UpdateFolderUseCase(folder_repository)


def get_delete_folder_use_case(
    folder_repository: Annotated[FolderRepository, Depends(get_folder_repository)],
) -> DeleteFolderUseCase:
    """Get delete folder use case with dependencies."""
    return DeleteFolderUseCase(folder_repository)


def get_assign_nodes_to_folder_use_case(
    folder_repository: Annotated[FolderRepository, Depends(get_folder_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AssignNodesToFolderUseCase:
    """Get assign nodes to folder use case with dependencies."""
    return AssignNodesToFolderUseCase(
        folder_repository, project_repository, space_repository, session
    )


@router.get(
    "/organizations/{organization_id}/folders",
    response_model=FolderListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_folders(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListFoldersUseCase, Depends(get_list_folders_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    parent_id: UUID | None = Query(None, description="Filter by parent folder ID"),
    include_deleted: bool = Query(default=False, description="Include soft-deleted folders"),
) -> FolderListResponse:
    """List folders in an organization.

    Requires the user to be a member of the organization.

    Args:
        organization_id: Organization UUID (from path)
        current_user: Current authenticated user
        use_case: List folders use case
        permission_service: Permission service
        parent_id: Optional parent folder ID to filter by
        include_deleted: Whether to include soft-deleted folders

    Returns:
        Folder list response

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
        parent_id=str(parent_id) if parent_id else None,
        include_deleted=include_deleted,
    )


@router.post(
    "/organizations/{organization_id}/folders",
    response_model=FolderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_folder(
    organization_id: UUID,
    request: CreateFolderRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[CreateFolderUseCase, Depends(get_create_folder_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> FolderResponse:
    """Create a new folder in an organization.

    Requires the user to be an admin of the organization.

    Args:
        organization_id: Organization UUID (from path)
        request: Folder creation request
        current_user: Current authenticated user
        use_case: Create folder use case
        permission_service: Permission service

    Returns:
        Created folder response

    Raises:
        HTTPException: If user is not an admin of the organization
    """
    # Verify user is an admin
    await require_organization_admin(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    # Ensure organization_id in request matches path
    request.organization_id = organization_id

    return await use_case.execute(request, str(current_user.id))


@router.get(
    "/organizations/{organization_id}/folders/{folder_id}",
    response_model=FolderResponse,
    status_code=status.HTTP_200_OK,
)
async def get_folder(
    organization_id: UUID,
    folder_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetFolderUseCase, Depends(get_get_folder_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> FolderResponse:
    """Get folder by ID.

    Requires the user to be a member of the organization.

    Args:
        organization_id: Organization UUID (from path)
        folder_id: Folder UUID (from path)
        current_user: Current authenticated user
        use_case: Get folder use case
        permission_service: Permission service

    Returns:
        Folder response

    Raises:
        HTTPException: If folder not found or user is not a member
    """
    # Verify user is a member
    await require_organization_member(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    return await use_case.execute(str(folder_id))


@router.put(
    "/organizations/{organization_id}/folders/{folder_id}",
    response_model=FolderResponse,
    status_code=status.HTTP_200_OK,
)
async def update_folder(
    organization_id: UUID,
    folder_id: UUID,
    request: UpdateFolderRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[UpdateFolderUseCase, Depends(get_update_folder_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> FolderResponse:
    """Update a folder.

    Requires the user to be an admin of the organization.

    Args:
        organization_id: Organization UUID (from path)
        folder_id: Folder UUID (from path)
        request: Folder update request
        current_user: Current authenticated user
        use_case: Update folder use case
        permission_service: Permission service

    Returns:
        Updated folder response

    Raises:
        HTTPException: If folder not found or user is not an admin
    """
    # Verify user is an admin
    await require_organization_admin(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    return await use_case.execute(str(folder_id), request)


@router.delete(
    "/organizations/{organization_id}/folders/{folder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_folder(
    organization_id: UUID,
    folder_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[DeleteFolderUseCase, Depends(get_delete_folder_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete a folder.

    Requires the user to be an admin of the organization.

    Args:
        organization_id: Organization UUID (from path)
        folder_id: Folder UUID (from path)
        current_user: Current authenticated user
        use_case: Delete folder use case
        permission_service: Permission service

    Raises:
        HTTPException: If folder not found or user is not an admin
    """
    # Verify user is an admin
    await require_organization_admin(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    await use_case.execute(str(folder_id))


@router.put(
    "/organizations/{organization_id}/folders/{folder_id}/nodes",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def assign_nodes_to_folder(
    organization_id: UUID,
    folder_id: UUID,
    request: AssignNodesToFolderRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[
        AssignNodesToFolderUseCase, Depends(get_assign_nodes_to_folder_use_case)
    ],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Assign nodes (projects/spaces) to a folder.

    Requires the user to be an admin of the organization.

    Args:
        organization_id: Organization UUID (from path)
        folder_id: Folder UUID (from path)
        request: Assignment request with node IDs
        current_user: Current authenticated user
        use_case: Assign nodes to folder use case
        permission_service: Permission service

    Raises:
        HTTPException: If folder or nodes not found, or user is not an admin
    """
    # Verify user is an admin
    await require_organization_admin(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    await use_case.execute(str(folder_id), request)

