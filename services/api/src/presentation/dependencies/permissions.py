"""Permission dependencies for FastAPI routes."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from src.domain.entities import User
from src.domain.services import PermissionService
from src.domain.value_objects import Role
from src.presentation.dependencies.auth import CurrentActiveUser
from src.presentation.dependencies.services import get_permission_service


async def require_organization_member(
    organization_id: UUID,
    current_user: CurrentActiveUser,
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> User:
    """Require user to be a member of the organization.
    
    Args:
        organization_id: Organization UUID to check
        current_user: Current authenticated user
        permission_service: Permission service instance
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If user is not a member of the organization
    """
    has_access = await permission_service.can_access_organization(
        current_user, organization_id
    )
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )
    
    return current_user


async def require_organization_admin(
    organization_id: UUID,
    current_user: CurrentActiveUser,
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> User:
    """Require user to be an admin of the organization.
    
    Args:
        organization_id: Organization UUID to check
        current_user: Current authenticated user
        permission_service: Permission service instance
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If user is not an admin of the organization
    """
    can_manage = await permission_service.can_manage_organization(
        current_user, organization_id
    )
    
    if not can_manage:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required for this operation",
        )
    
    return current_user


async def require_project_access(
    project_id: UUID,
    current_user: CurrentActiveUser,
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> User:
    """Require user to have access to the project.
    
    Args:
        project_id: Project UUID to check
        current_user: Current authenticated user
        permission_service: Permission service instance
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If user cannot access the project
    """
    has_access = await permission_service.can_access_project(
        current_user, project_id
    )
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        )
    
    return current_user


async def require_edit_permission(
    organization_id: UUID,
    current_user: CurrentActiveUser,
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    project_id: UUID | None = None,
) -> User:
    """Require user to have edit permissions.
    
    Args:
        organization_id: Organization UUID
        current_user: Current authenticated user
        permission_service: Permission service instance
        project_id: Optional project UUID for project-specific checks
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If user does not have edit permissions
    """
    can_edit = await permission_service.can_edit_content(
        current_user, organization_id, project_id
    )
    
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this content",
        )
    
    return current_user


async def get_organization_role(
    organization_id: UUID,
    current_user: CurrentActiveUser,
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> Role:
    """Get user's role in an organization.
    
    Args:
        organization_id: Organization UUID
        current_user: Current authenticated user
        permission_service: Permission service instance
        
    Returns:
        User's role in the organization
        
    Raises:
        HTTPException: If user is not a member
    """
    role = await permission_service.get_organization_role(
        current_user.id, organization_id
    )
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )
    
    return role

