"""Issue management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.issue import (
    CreateIssueRequest,
    IssueListResponse,
    IssueResponse,
    UpdateIssueRequest,
)
from src.application.dtos.issue_activity import IssueActivityListResponse
from src.application.use_cases.issue import (
    CreateIssueUseCase,
    DeleteIssueUseCase,
    GetIssueUseCase,
    ListIssueActivitiesUseCase,
    ListIssuesUseCase,
    UpdateIssueUseCase,
)
from src.domain.entities import User
from src.domain.repositories import (
    IssueActivityRepository,
    IssueRepository,
    ProjectRepository,
    UserRepository,
)
from src.domain.services import PermissionService
from src.infrastructure.database import get_session
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import (
    require_edit_permission,
    require_organization_member,
)
from src.presentation.dependencies.services import (
    get_issue_activity_repository,
    get_issue_repository,
    get_permission_service,
    get_project_repository,
    get_user_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_create_issue_use_case(
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    activity_repository: Annotated[IssueActivityRepository, Depends(get_issue_activity_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateIssueUseCase:
    """Get create issue use case with dependencies."""
    return CreateIssueUseCase(
        issue_repository, project_repository, user_repository, activity_repository, session
    )


def get_issue_use_case(
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetIssueUseCase:
    """Get issue use case with dependencies."""
    return GetIssueUseCase(issue_repository, project_repository, session)


def get_list_issues_use_case(
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListIssuesUseCase:
    """Get list issues use case with dependencies."""
    return ListIssuesUseCase(issue_repository, project_repository, session)


def get_update_issue_use_case(
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    activity_repository: Annotated[IssueActivityRepository, Depends(get_issue_activity_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UpdateIssueUseCase:
    """Get update issue use case with dependencies."""
    return UpdateIssueUseCase(
        issue_repository, project_repository, user_repository, activity_repository, session
    )


def get_delete_issue_use_case(
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    activity_repository: Annotated[IssueActivityRepository, Depends(get_issue_activity_repository)],
) -> DeleteIssueUseCase:
    """Get delete issue use case with dependencies."""
    return DeleteIssueUseCase(issue_repository, activity_repository)


def get_list_issue_activities_use_case(
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    activity_repository: Annotated[IssueActivityRepository, Depends(get_issue_activity_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListIssueActivitiesUseCase:
    """Get list issue activities use case with dependencies."""
    return ListIssueActivitiesUseCase(issue_repository, activity_repository, session)


@router.post("/", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: CreateIssueRequest,
    use_case: Annotated[CreateIssueUseCase, Depends(get_create_issue_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> IssueResponse:
    """Create a new issue.

    Requires project membership (via organization membership).
    """
    from fastapi import HTTPException

    # Verify project exists and user has edit permissions
    project = await project_repository.get_by_id(request.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    return await use_case.execute(request, str(current_user.id))


@router.get("/{issue_id}", response_model=IssueResponse, status_code=status.HTTP_200_OK)
async def get_issue(
    current_user: Annotated[User, Depends(get_current_active_user)],
    issue_id: UUID,
    use_case: Annotated[GetIssueUseCase, Depends(get_issue_use_case)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> IssueResponse:
    """Get issue by ID.

    Requires project membership (via organization membership).
    """
    from fastapi import HTTPException

    issue = await issue_repository.get_by_id(issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Check user is member of the organization
    project = await project_repository.get_by_id(issue.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_organization_member(project.organization_id, current_user, permission_service)

    return await use_case.execute(str(issue_id))


@router.get("/", response_model=IssueListResponse, status_code=status.HTTP_200_OK)
async def list_issues(
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_id: Annotated[UUID, Query(..., description="Project ID")],
    use_case: Annotated[ListIssuesUseCase, Depends(get_list_issues_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of issues per page")] = 20,
    search: Annotated[str | None, Query(description="Search query (title or description)")] = None,
    assignee_id: Annotated[UUID | None, Query(description="Filter by assignee ID")] = None,
    reporter_id: Annotated[UUID | None, Query(description="Filter by reporter ID")] = None,
    status: Annotated[str | None, Query(description="Filter by status")] = None,
    type: Annotated[str | None, Query(description="Filter by type")] = None,
    priority: Annotated[str | None, Query(description="Filter by priority")] = None,
) -> IssueListResponse:
    """List issues in a project.

    Requires project membership (via organization membership).
    """
    from fastapi import HTTPException

    # Check user is member of the organization
    project = await project_repository.get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_organization_member(project.organization_id, current_user, permission_service)

    return await use_case.execute(
        str(project_id),
        page=page,
        limit=limit,
        search=search,
        assignee_id=str(assignee_id) if assignee_id else None,
        reporter_id=str(reporter_id) if reporter_id else None,
        status=status,
        type=type,
        priority=priority,
    )


@router.put("/{issue_id}", response_model=IssueResponse, status_code=status.HTTP_200_OK)
async def update_issue(
    current_user: Annotated[User, Depends(get_current_active_user)],
    issue_id: UUID,
    request: UpdateIssueRequest,
    use_case: Annotated[UpdateIssueUseCase, Depends(get_update_issue_use_case)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> IssueResponse:
    """Update an issue.

    Requires project membership (via organization membership).
    """
    from fastapi import HTTPException

    issue = await issue_repository.get_by_id(issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Check user has edit permissions
    project = await project_repository.get_by_id(issue.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    return await use_case.execute(str(issue_id), request, current_user.id)


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    current_user: Annotated[User, Depends(get_current_active_user)],
    issue_id: UUID,
    use_case: Annotated[DeleteIssueUseCase, Depends(get_delete_issue_use_case)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete an issue (soft delete).

    Requires project membership (via organization membership).
    """
    from fastapi import HTTPException

    issue = await issue_repository.get_by_id(issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Check user has edit permissions
    project = await project_repository.get_by_id(issue.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    await use_case.execute(str(issue_id), current_user.id)


@router.get(
    "/{issue_id}/activities",
    response_model=IssueActivityListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_issue_activities(
    current_user: Annotated[User, Depends(get_current_active_user)],
    issue_id: UUID,
    use_case: Annotated[ListIssueActivitiesUseCase, Depends(get_list_issue_activities_use_case)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of activities per page")] = 50,
) -> IssueActivityListResponse:
    """List activities for an issue.

    Requires project membership (via organization membership).
    """
    from fastapi import HTTPException

    issue = await issue_repository.get_by_id(issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Check user is member of the organization
    project = await project_repository.get_by_id(issue.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_organization_member(project.organization_id, current_user, permission_service)

    return await use_case.execute(str(issue_id), page=page, limit=limit)
