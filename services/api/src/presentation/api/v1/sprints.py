"""Sprint management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.sprint import (
    AddIssueToSprintRequest,
    CreateSprintRequest,
    ReorderSprintIssuesRequest,
    SprintListResponse,
    SprintResponse,
    SprintWithIssuesResponse,
    UpdateSprintRequest,
)
from src.application.dtos.sprint_metrics import (
    CompleteSprintRequest,
    CompleteSprintResponse,
    SprintMetricsResponse,
)
from src.application.use_cases.sprint import (
    AddIssueToSprintUseCase,
    CompleteSprintUseCase,
    CreateSprintUseCase,
    DeleteSprintUseCase,
    GetSprintMetricsUseCase,
    GetSprintUseCase,
    ListSprintsUseCase,
    RemoveIssueFromSprintUseCase,
    ReorderSprintIssuesUseCase,
    UpdateSprintUseCase,
)
from src.domain.entities import User
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import (
    IssueRepository,
    ProjectRepository,
    SprintRepository,
)
from src.domain.value_objects.sprint_status import SprintStatus
from src.infrastructure.database import get_session
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.services import (
    get_issue_repository,
    get_project_repository,
    get_sprint_repository,
)

router = APIRouter(tags=["Sprints"])


# Dependency injection for use cases
def get_create_sprint_use_case(
    sprint_repository: Annotated[SprintRepository, Depends(get_sprint_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> CreateSprintUseCase:
    """Get create sprint use case with dependencies."""
    return CreateSprintUseCase(sprint_repository, project_repository)


def get_get_sprint_use_case(
    sprint_repository: Annotated[SprintRepository, Depends(get_sprint_repository)],
) -> GetSprintUseCase:
    """Get sprint use case with dependencies."""
    return GetSprintUseCase(sprint_repository)


def get_list_sprints_use_case(
    sprint_repository: Annotated[SprintRepository, Depends(get_sprint_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> ListSprintsUseCase:
    """Get list sprints use case with dependencies."""
    return ListSprintsUseCase(sprint_repository, project_repository)


def get_update_sprint_use_case(
    sprint_repository: Annotated[SprintRepository, Depends(get_sprint_repository)],
) -> UpdateSprintUseCase:
    """Get update sprint use case with dependencies."""
    return UpdateSprintUseCase(sprint_repository)


def get_delete_sprint_use_case(
    sprint_repository: Annotated[SprintRepository, Depends(get_sprint_repository)],
) -> DeleteSprintUseCase:
    """Get delete sprint use case with dependencies."""
    return DeleteSprintUseCase(sprint_repository)


def get_add_issue_to_sprint_use_case(
    sprint_repository: Annotated[SprintRepository, Depends(get_sprint_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
) -> AddIssueToSprintUseCase:
    """Get add issue to sprint use case with dependencies."""
    return AddIssueToSprintUseCase(sprint_repository, issue_repository)


def get_remove_issue_from_sprint_use_case(
    sprint_repository: Annotated[SprintRepository, Depends(get_sprint_repository)],
) -> RemoveIssueFromSprintUseCase:
    """Get remove issue from sprint use case with dependencies."""
    return RemoveIssueFromSprintUseCase(sprint_repository)


def get_reorder_sprint_issues_use_case(
    sprint_repository: Annotated[SprintRepository, Depends(get_sprint_repository)],
) -> ReorderSprintIssuesUseCase:
    """Get reorder sprint issues use case with dependencies."""
    return ReorderSprintIssuesUseCase(sprint_repository)


def get_get_sprint_metrics_use_case(
    sprint_repository: Annotated[SprintRepository, Depends(get_sprint_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetSprintMetricsUseCase:
    """Get sprint metrics use case with dependencies."""
    return GetSprintMetricsUseCase(sprint_repository, issue_repository, session)


def get_complete_sprint_use_case(
    sprint_repository: Annotated[SprintRepository, Depends(get_sprint_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CompleteSprintUseCase:
    """Get complete sprint use case with dependencies."""
    return CompleteSprintUseCase(sprint_repository, issue_repository, session)


@router.post(
    "/projects/{project_id}/sprints",
    response_model=SprintResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new sprint",
    description="Create a new sprint in a project",
)
async def create_sprint(
    project_id: UUID,
    request: CreateSprintRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[CreateSprintUseCase, Depends(get_create_sprint_use_case)],
) -> SprintResponse:
    """Create a new sprint in a project.

    Args:
        project_id: Project UUID
        request: Sprint creation request
        current_user: Current authenticated user
        use_case: Create sprint use case

    Returns:
        Created sprint response

    Raises:
        HTTPException: If project not found or dates overlap
    """
    try:
        return await use_case.execute(project_id, request)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/sprints/{sprint_id}",
    response_model=SprintWithIssuesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get sprint by ID",
    description="Get a sprint by its ID with issues",
)
async def get_sprint(
    sprint_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetSprintUseCase, Depends(get_get_sprint_use_case)],
) -> SprintWithIssuesResponse:
    """Get a sprint by ID.

    Args:
        sprint_id: Sprint UUID
        current_user: Current authenticated user
        use_case: Get sprint use case

    Returns:
        Sprint response with issues

    Raises:
        HTTPException: If sprint not found
    """
    try:
        return await use_case.execute(sprint_id)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get(
    "/projects/{project_id}/sprints",
    response_model=SprintListResponse,
    status_code=status.HTTP_200_OK,
    summary="List sprints in a project",
    description="Get a paginated list of sprints in a project",
)
async def list_sprints(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListSprintsUseCase, Depends(get_list_sprints_use_case)],
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    status_filter: Annotated[
        SprintStatus | None, Query(description="Filter by sprint status")
    ] = None,
) -> SprintListResponse:
    """List sprints in a project.

    Args:
        project_id: Project UUID
        page: Page number (1-indexed)
        limit: Number of items per page
        status_filter: Optional status filter
        current_user: Current authenticated user
        use_case: List sprints use case

    Returns:
        Paginated sprint list response

    Raises:
        HTTPException: If project not found
    """
    try:
        return await use_case.execute(project_id, page, limit, status_filter)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.put(
    "/sprints/{sprint_id}",
    response_model=SprintResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a sprint",
    description="Update sprint information",
)
async def update_sprint(
    sprint_id: UUID,
    request: UpdateSprintRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[UpdateSprintUseCase, Depends(get_update_sprint_use_case)],
) -> SprintResponse:
    """Update a sprint.

    Args:
        sprint_id: Sprint UUID
        request: Sprint update request
        current_user: Current authenticated user
        use_case: Update sprint use case

    Returns:
        Updated sprint response

    Raises:
        HTTPException: If sprint not found or dates overlap
    """
    try:
        return await use_case.execute(sprint_id, request)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/sprints/{sprint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a sprint",
    description="Delete a sprint (hard delete)",
)
async def delete_sprint(
    sprint_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[DeleteSprintUseCase, Depends(get_delete_sprint_use_case)],
) -> Response:
    """Delete a sprint.

    Args:
        sprint_id: Sprint UUID
        current_user: Current authenticated user
        use_case: Delete sprint use case

    Returns:
        Empty response with 204 status

    Raises:
        HTTPException: If sprint not found
    """
    try:
        await use_case.execute(sprint_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.put(
    "/sprints/{sprint_id}/issues",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Add issue to sprint",
    description="Add an issue to a sprint",
)
async def add_issue_to_sprint(
    sprint_id: UUID,
    request: AddIssueToSprintRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[AddIssueToSprintUseCase, Depends(get_add_issue_to_sprint_use_case)],
) -> Response:
    """Add an issue to a sprint.

    Args:
        sprint_id: Sprint UUID
        request: Add issue to sprint request
        current_user: Current authenticated user
        use_case: Add issue to sprint use case

    Returns:
        Empty response with 204 status

    Raises:
        HTTPException: If sprint or issue not found, or conflict occurs
    """
    try:
        await use_case.execute(sprint_id, request.issue_id, request.order)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e


@router.delete(
    "/sprints/{sprint_id}/issues/{issue_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove issue from sprint",
    description="Remove an issue from a sprint",
)
async def remove_issue_from_sprint(
    sprint_id: UUID,
    issue_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[
        RemoveIssueFromSprintUseCase, Depends(get_remove_issue_from_sprint_use_case)
    ],
) -> Response:
    """Remove an issue from a sprint.

    Args:
        sprint_id: Sprint UUID
        issue_id: Issue UUID
        current_user: Current authenticated user
        use_case: Remove issue from sprint use case

    Returns:
        Empty response with 204 status

    Raises:
        HTTPException: If sprint or issue not found, or issue not in sprint
    """
    try:
        await use_case.execute(sprint_id, issue_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.put(
    "/sprints/{sprint_id}/issues/reorder",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reorder sprint issues",
    description="Reorder issues within a sprint",
)
async def reorder_sprint_issues(
    sprint_id: UUID,
    request: ReorderSprintIssuesRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ReorderSprintIssuesUseCase, Depends(get_reorder_sprint_issues_use_case)],
) -> Response:
    """Reorder issues within a sprint.

    Args:
        sprint_id: Sprint UUID
        request: Reorder sprint issues request
        current_user: Current authenticated user
        use_case: Reorder sprint issues use case

    Returns:
        Empty response with 204 status

    Raises:
        HTTPException: If sprint not found
    """
    try:
        # Convert string keys to UUID
        issue_orders = {UUID(k): v for k, v in request.issue_orders.items()}
        await use_case.execute(sprint_id, issue_orders)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/sprints/{sprint_id}/metrics",
    response_model=SprintMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get sprint metrics",
    description="Get metrics for a sprint (velocity, completion, burndown)",
)
async def get_sprint_metrics(
    sprint_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetSprintMetricsUseCase, Depends(get_get_sprint_metrics_use_case)],
) -> SprintMetricsResponse:
    """Get sprint metrics.

    Args:
        sprint_id: Sprint UUID
        current_user: Current authenticated user
        use_case: Get sprint metrics use case

    Returns:
        Sprint metrics response

    Raises:
        HTTPException: If sprint not found
    """
    try:
        return await use_case.execute(sprint_id)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.post(
    "/sprints/{sprint_id}/complete",
    response_model=CompleteSprintResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete a sprint",
    description="Mark a sprint as completed and optionally move incomplete issues to backlog",
)
async def complete_sprint(
    sprint_id: UUID,
    request: CompleteSprintRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[CompleteSprintUseCase, Depends(get_complete_sprint_use_case)],
) -> CompleteSprintResponse:
    """Complete a sprint.

    Args:
        sprint_id: Sprint UUID
        request: Complete sprint request
        current_user: Current authenticated user
        use_case: Complete sprint use case

    Returns:
        Complete sprint response with metrics

    Raises:
        HTTPException: If sprint not found
    """
    try:
        return await use_case.execute(sprint_id, request)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
