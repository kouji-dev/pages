"""Node management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.node import NodeListResponse
from src.application.use_cases.node import ListNodesUseCase
from src.domain.entities import User
from src.domain.repositories import ProjectRepository, SpaceRepository
from src.domain.services import PermissionService
from src.infrastructure.database import get_session
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_organization_member
from src.presentation.dependencies.services import (
    get_permission_service,
    get_project_repository,
    get_space_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_list_nodes_use_case(
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListNodesUseCase:
    """Get list nodes use case with dependencies."""
    return ListNodesUseCase(project_repository, space_repository, session)


@router.get(
    "/organizations/{organization_id}/nodes",
    response_model=NodeListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_nodes(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListNodesUseCase, Depends(get_list_nodes_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    folder_id: UUID | None = Query(None, description="Filter nodes by folder ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
) -> NodeListResponse:
    """List nodes (projects + spaces) in an organization.

    Requires the user to be a member of the organization.

    Args:
        organization_id: Organization UUID (from path)
        current_user: Current authenticated user
        use_case: List nodes use case
        permission_service: Permission service
        folder_id: Optional folder ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Node list response

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
        skip=skip,
        limit=limit,
    )
