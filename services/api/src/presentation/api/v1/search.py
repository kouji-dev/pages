"""Search API endpoints."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.application.dtos.search import SearchResponse
from src.application.services.search_query_service import SearchQueryService
from src.application.use_cases.search.search_all import SearchAllUseCase
from src.application.use_cases.search.search_issues import SearchIssuesUseCase
from src.application.use_cases.search.search_pages import SearchPagesUseCase
from src.domain.entities import User
from src.domain.repositories import ProjectRepository, SpaceRepository
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_organization_member
from src.presentation.dependencies.services import (
    get_permission_service,
    get_project_repository,
    get_search_query_service,
    get_space_repository,
)

router = APIRouter(tags=["Search"])


def get_search_all_use_case(
    search_service: Annotated[SearchQueryService, Depends(get_search_query_service)],
) -> SearchAllUseCase:
    return SearchAllUseCase(search_service)


def get_search_issues_use_case(
    search_service: Annotated[SearchQueryService, Depends(get_search_query_service)],
) -> SearchIssuesUseCase:
    return SearchIssuesUseCase(search_service)


def get_search_pages_use_case(
    search_service: Annotated[SearchQueryService, Depends(get_search_query_service)],
) -> SearchPagesUseCase:
    return SearchPagesUseCase(search_service)


@router.get("/search", response_model=SearchResponse, status_code=status.HTTP_200_OK)
async def unified_search(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[SearchAllUseCase, Depends(get_search_all_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    query: Annotated[str, Query(..., description="Search term")],
    type: Annotated[Literal["all", "issues", "pages"], Query()] = "all",
    project_id: Annotated[UUID | None, Query(description="Project ID filter")] = None,
    space_id: Annotated[UUID | None, Query(description="Space ID filter")] = None,
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of items per page")] = 20,
    assignee_id: Annotated[UUID | None, Query(description="Filter by assignee ID")] = None,
    reporter_id: Annotated[UUID | None, Query(description="Filter by reporter ID")] = None,
    status: Annotated[str | None, Query(description="Filter by status")] = None,
    issue_type: Annotated[
        str | None, Query(alias="issue_type", description="Filter by issue type")
    ] = None,
    priority: Annotated[str | None, Query(description="Filter by priority")] = None,
) -> SearchResponse:
    """Unified search across issues and pages."""
    # Validate permissions
    if type in ("all", "issues"):
        if project_id is None:
            raise ValueError("project_id is required when searching issues")
        project = await project_repository.get_by_id(project_id)
        if project is None:
            raise ValueError("Project not found")
        await require_organization_member(project.organization_id, current_user, permission_service)

    if type in ("all", "pages"):
        if space_id is None:
            raise ValueError("space_id is required when searching pages")
        space = await space_repository.get_by_id(space_id)
        if space is None:
            raise ValueError("Space not found")
        await require_organization_member(space.organization_id, current_user, permission_service)

    return await use_case.execute(
        query=query,
        search_type=type,
        project_id=project_id,
        space_id=space_id,
        page=page,
        limit=limit,
        assignee_id=assignee_id,
        reporter_id=reporter_id,
        status=status,
        type=issue_type,
        priority=priority,
    )


@router.get(
    "/issues/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
)
async def search_issues(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[SearchIssuesUseCase, Depends(get_search_issues_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    project_id: Annotated[UUID, Query(..., description="Project ID")],
    query: Annotated[str, Query(..., description="Search term")],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of items per page")] = 20,
    assignee_id: Annotated[UUID | None, Query(description="Filter by assignee ID")] = None,
    reporter_id: Annotated[UUID | None, Query(description="Filter by reporter ID")] = None,
    status: Annotated[str | None, Query(description="Filter by status")] = None,
    issue_type: Annotated[
        str | None, Query(alias="issue_type", description="Filter by issue type")
    ] = None,
    priority: Annotated[str | None, Query(description="Filter by priority")] = None,
) -> SearchResponse:
    """Search issues within a project."""
    project = await project_repository.get_by_id(project_id)
    if project is None:
        raise ValueError("Project not found")

    await require_organization_member(project.organization_id, current_user, permission_service)

    return await use_case.execute(
        project_id=project_id,
        query=query,
        page=page,
        limit=limit,
        assignee_id=assignee_id,
        reporter_id=reporter_id,
        status=status,
        type=issue_type,
        priority=priority,
    )


@router.get(
    "/pages/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
)
async def search_pages(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[SearchPagesUseCase, Depends(get_search_pages_use_case)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    space_id: Annotated[UUID, Query(..., description="Space ID")],
    query: Annotated[str, Query(..., description="Search term")],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of items per page")] = 20,
) -> SearchResponse:
    """Search pages within a space."""
    space = await space_repository.get_by_id(space_id)
    if space is None:
        raise ValueError("Space not found")

    await require_organization_member(space.organization_id, current_user, permission_service)

    return await use_case.execute(space_id=space_id, query=query, page=page, limit=limit)
