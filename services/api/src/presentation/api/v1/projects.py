"""Project management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.project import (
    CreateProjectRequest,
    ProjectListResponse,
    ProjectResponse,
    UpdateProjectRequest,
)
from src.application.dtos.project_member import (
    AddProjectMemberRequest,
    ProjectMemberListResponse,
    ProjectMemberResponse,
    UpdateProjectMemberRoleRequest,
)
from src.application.use_cases.project import (
    AddProjectMemberUseCase,
    CreateProjectUseCase,
    DeleteProjectUseCase,
    GetProjectUseCase,
    ListProjectMembersUseCase,
    ListProjectsUseCase,
    RemoveProjectMemberUseCase,
    UpdateProjectMemberRoleUseCase,
    UpdateProjectUseCase,
)
from src.domain.entities import User
from src.domain.repositories import (
    OrganizationRepository,
    ProjectRepository,
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
    get_organization_repository,
    get_permission_service,
    get_project_repository,
    get_user_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_create_project_use_case(
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateProjectUseCase:
    """Get create project use case with dependencies."""
    return CreateProjectUseCase(
        project_repository, organization_repository, user_repository, session
    )


def get_project_use_case(
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetProjectUseCase:
    """Get project use case with dependencies."""
    return GetProjectUseCase(project_repository, session)


def get_list_projects_use_case(
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListProjectsUseCase:
    """Get list projects use case with dependencies."""
    return ListProjectsUseCase(project_repository, session)


def get_update_project_use_case(
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UpdateProjectUseCase:
    """Get update project use case with dependencies."""
    return UpdateProjectUseCase(project_repository, session)


def get_delete_project_use_case(
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> DeleteProjectUseCase:
    """Get delete project use case with dependencies."""
    return DeleteProjectUseCase(project_repository)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: CreateProjectRequest,
    use_case: Annotated[CreateProjectUseCase, Depends(get_create_project_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> ProjectResponse:
    """Create a new project.

    Requires organization membership.
    """
    # Check user has edit permissions
    await require_edit_permission(request.organization_id, current_user, permission_service)

    return await use_case.execute(request, str(current_user.id))


@router.get("/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
async def get_project(
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_id: UUID,
    use_case: Annotated[GetProjectUseCase, Depends(get_project_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> ProjectResponse:
    """Get project by ID.

    Requires project membership (via organization membership).
    """
    from fastapi import HTTPException

    project = await project_repository.get_by_id(project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check user is member of the organization
    await require_organization_member(project.organization_id, current_user, permission_service)

    return await use_case.execute(str(project_id))


@router.get("/", response_model=ProjectListResponse, status_code=status.HTTP_200_OK)
async def list_projects(
    current_user: Annotated[User, Depends(get_current_active_user)],
    organization_id: Annotated[UUID, Query(..., description="Organization ID")],
    use_case: Annotated[ListProjectsUseCase, Depends(get_list_projects_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of projects per page")] = 20,
    search: Annotated[str | None, Query(description="Search query (name or key)")] = None,
) -> ProjectListResponse:
    """List projects in an organization.

    Requires organization membership.
    """
    # Check user is member of the organization
    await require_organization_member(organization_id, current_user, permission_service)

    return await use_case.execute(
        str(organization_id),
        page=page,
        limit=limit,
        search=search,
    )


@router.put("/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
async def update_project(
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_id: UUID,
    request: UpdateProjectRequest,
    use_case: Annotated[UpdateProjectUseCase, Depends(get_update_project_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> ProjectResponse:
    """Update a project.

    Requires project membership (via organization membership).
    """
    from fastapi import HTTPException

    project = await project_repository.get_by_id(project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check user has edit permissions
    await require_edit_permission(project.organization_id, current_user, permission_service)

    return await use_case.execute(str(project_id), request)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_id: UUID,
    use_case: Annotated[DeleteProjectUseCase, Depends(get_delete_project_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete a project (soft delete).

    Requires organization admin role.
    """
    from fastapi import HTTPException

    from src.presentation.dependencies.permissions import require_organization_admin

    project = await project_repository.get_by_id(project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check user is admin of the organization
    await require_organization_admin(project.organization_id, current_user, permission_service)

    await use_case.execute(str(project_id))


# Project member management endpoints
def get_add_project_member_use_case(
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AddProjectMemberUseCase:
    """Get add project member use case with dependencies."""
    return AddProjectMemberUseCase(project_repository, user_repository, session)


def get_list_project_members_use_case(
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListProjectMembersUseCase:
    """Get list project members use case with dependencies."""
    return ListProjectMembersUseCase(project_repository, session)


def get_update_project_member_role_use_case(
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UpdateProjectMemberRoleUseCase:
    """Get update project member role use case with dependencies."""
    return UpdateProjectMemberRoleUseCase(project_repository, user_repository, session)


def get_remove_project_member_use_case(
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RemoveProjectMemberUseCase:
    """Get remove project member use case with dependencies."""
    return RemoveProjectMemberUseCase(project_repository, session)


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_project_member(
    project_id: UUID,
    request: AddProjectMemberRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[AddProjectMemberUseCase, Depends(get_add_project_member_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> ProjectMemberResponse:
    """Add a member to a project.

    Requires admin role in the project's organization.
    """
    from fastapi import HTTPException

    project = await project_repository.get_by_id(project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify user is admin of the organization
    await require_organization_admin(project.organization_id, current_user, permission_service)

    return await use_case.execute(str(project_id), request)


@router.get(
    "/{project_id}/members",
    response_model=ProjectMemberListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_project_members(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListProjectMembersUseCase, Depends(get_list_project_members_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of members per page")] = 20,
    search: Annotated[
        str | None, Query(description="Search query (filters by name or email)")
    ] = None,
) -> ProjectMemberListResponse:
    """List members of a project.

    Requires user to be a member of the project's organization.
    Supports searching by user name or email.
    """
    from fastapi import HTTPException

    project = await project_repository.get_by_id(project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify user is a member of the organization
    await require_organization_member(project.organization_id, current_user, permission_service)

    return await use_case.execute(str(project_id), page=page, limit=limit, search=search)


@router.put(
    "/{project_id}/members/{user_id}",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_200_OK,
)
async def update_project_member_role(
    project_id: UUID,
    user_id: UUID,
    request: UpdateProjectMemberRoleRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[
        UpdateProjectMemberRoleUseCase, Depends(get_update_project_member_role_use_case)
    ],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> ProjectMemberResponse:
    """Update a project member's role.

    Requires admin role in the project's organization.
    """
    from fastapi import HTTPException

    project = await project_repository.get_by_id(project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify user is admin of the organization
    await require_organization_admin(project.organization_id, current_user, permission_service)

    return await use_case.execute(str(project_id), str(user_id), request)


@router.delete(
    "/{project_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[RemoveProjectMemberUseCase, Depends(get_remove_project_member_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Remove a member from a project.

    Requires admin role in the project's organization.
    """
    from fastapi import HTTPException

    project = await project_repository.get_by_id(project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify user is admin of the organization
    await require_organization_admin(project.organization_id, current_user, permission_service)

    await use_case.execute(str(project_id), str(user_id))
