"""Backlog management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.backlog import (
    BacklogListResponse,
    PrioritizeBacklogRequest,
    ReorderBacklogIssueRequest,
)
from src.application.use_cases.backlog import (
    ListBacklogUseCase,
    PrioritizeBacklogUseCase,
    ReorderBacklogIssueUseCase,
)
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    IssueRepository,
    ProjectRepository,
    SprintRepository,
)
from src.infrastructure.database import get_session
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.services import (
    get_issue_repository,
    get_project_repository,
    get_sprint_repository,
)

router = APIRouter(tags=["Backlog"])


# Dependency injection for use cases
def get_list_backlog_use_case(
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    sprint_repository: Annotated[SprintRepository, Depends(get_sprint_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListBacklogUseCase:
    """Get list backlog use case with dependencies."""
    return ListBacklogUseCase(issue_repository, sprint_repository, project_repository, session)


def get_prioritize_backlog_use_case(
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PrioritizeBacklogUseCase:
    """Get prioritize backlog use case with dependencies."""
    return PrioritizeBacklogUseCase(project_repository, session)


def get_reorder_backlog_issue_use_case(
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    sprint_repository: Annotated[SprintRepository, Depends(get_sprint_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReorderBacklogIssueUseCase:
    """Get reorder backlog issue use case with dependencies."""
    return ReorderBacklogIssueUseCase(project_repository, sprint_repository, session)


@router.get(
    "/projects/{project_id}/backlog",
    response_model=BacklogListResponse,
    status_code=status.HTTP_200_OK,
    summary="List backlog issues",
    description="Get a paginated list of issues in the backlog (not in any sprint)",
)
async def list_backlog(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListBacklogUseCase, Depends(get_list_backlog_use_case)],
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    type_filter: Annotated[str | None, Query(description="Filter by issue type")] = None,
    assignee_id: Annotated[UUID | None, Query(description="Filter by assignee ID")] = None,
    priority_filter: Annotated[str | None, Query(description="Filter by priority")] = None,
    sort_by: Annotated[
        str,
        Query(description="Sort field: backlog_order, created_at, updated_at, priority"),
    ] = "backlog_order",
) -> BacklogListResponse:
    """List backlog issues.

    Args:
        project_id: Project UUID
        page: Page number (1-indexed)
        limit: Number of items per page
        type_filter: Optional issue type filter
        assignee_id: Optional assignee filter
        priority_filter: Optional priority filter
        sort_by: Sort field
        current_user: Current authenticated user
        use_case: List backlog use case

    Returns:
        Paginated backlog list response

    Raises:
        HTTPException: If project not found
    """
    try:
        return await use_case.execute(
            project_id,
            page,
            limit,
            type_filter,
            assignee_id,
            priority_filter,
            sort_by,
        )
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.put(
    "/projects/{project_id}/backlog/prioritize",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Prioritize backlog",
    description="Set the priority order of issues in the backlog",
)
async def prioritize_backlog(
    project_id: UUID,
    request: PrioritizeBacklogRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[PrioritizeBacklogUseCase, Depends(get_prioritize_backlog_use_case)],
) -> Response:
    """Prioritize backlog issues.

    Args:
        project_id: Project UUID
        request: Prioritize backlog request
        current_user: Current authenticated user
        use_case: Prioritize backlog use case

    Returns:
        Empty response with 204 status

    Raises:
        HTTPException: If project not found
    """
    try:
        await use_case.execute(project_id, request)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.put(
    "/projects/{project_id}/backlog/issues/{issue_id}/reorder",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reorder single backlog issue",
    description="Move a single issue to a specific position in the backlog",
)
async def reorder_backlog_issue(
    project_id: UUID,
    issue_id: UUID,
    request: ReorderBacklogIssueRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ReorderBacklogIssueUseCase, Depends(get_reorder_backlog_issue_use_case)],
) -> Response:
    """Reorder a single backlog issue.

    Args:
        project_id: Project UUID
        issue_id: Issue UUID
        request: Reorder backlog issue request
        current_user: Current authenticated user
        use_case: Reorder backlog issue use case

    Returns:
        Empty response with 204 status

    Raises:
        HTTPException: If project or issue not found, or issue is in a sprint
    """
    try:
        await use_case.execute(project_id, issue_id, request)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
