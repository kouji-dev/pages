"""Issue link management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.issue_link import (
    CreateIssueLinkRequest,
    IssueLinkListResponse,
    IssueLinkResponse,
)
from src.application.use_cases.issue_link import (
    CreateIssueLinkUseCase,
    DeleteIssueLinkUseCase,
    ListIssueLinksUseCase,
)
from src.domain.entities import User
from src.domain.repositories import IssueRepository, ProjectRepository
from src.domain.repositories.issue_link_repository import IssueLinkRepository
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_edit_permission
from src.presentation.dependencies.services import (
    get_issue_link_repository,
    get_issue_repository,
    get_permission_service,
    get_project_repository,
)

router = APIRouter(tags=["Issue Links"])


def get_create_issue_link_use_case(
    issue_link_repository: Annotated[IssueLinkRepository, Depends(get_issue_link_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
) -> CreateIssueLinkUseCase:
    """Get create issue link use case."""
    return CreateIssueLinkUseCase(issue_link_repository, issue_repository)


def get_list_issue_links_use_case(
    issue_link_repository: Annotated[IssueLinkRepository, Depends(get_issue_link_repository)],
) -> ListIssueLinksUseCase:
    """Get list issue links use case."""
    return ListIssueLinksUseCase(issue_link_repository)


def get_delete_issue_link_use_case(
    issue_link_repository: Annotated[IssueLinkRepository, Depends(get_issue_link_repository)],
) -> DeleteIssueLinkUseCase:
    """Get delete issue link use case."""
    return DeleteIssueLinkUseCase(issue_link_repository)


@router.post(
    "/issues/{issue_id}/links",
    response_model=IssueLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create issue link",
)
async def create_issue_link(
    current_user: Annotated[User, Depends(get_current_active_user)],
    issue_id: UUID,
    request: CreateIssueLinkRequest,
    use_case: Annotated[CreateIssueLinkUseCase, Depends(get_create_issue_link_use_case)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> IssueLinkResponse:
    """Create a new issue link."""
    issue = await issue_repository.get_by_id(issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    project = await project_repository.get_by_id(issue.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    try:
        return await use_case.execute(issue_id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/issues/{issue_id}/links",
    response_model=IssueLinkListResponse,
    status_code=status.HTTP_200_OK,
    summary="List issue links",
)
async def list_issue_links(
    current_user: Annotated[User, Depends(get_current_active_user)],
    issue_id: UUID,
    use_case: Annotated[ListIssueLinksUseCase, Depends(get_list_issue_links_use_case)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> IssueLinkListResponse:
    """List all links for an issue."""
    issue = await issue_repository.get_by_id(issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    project = await project_repository.get_by_id(issue.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    return await use_case.execute(issue_id)


@router.delete(
    "/issue-links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete issue link",
)
async def delete_issue_link(
    current_user: Annotated[User, Depends(get_current_active_user)],
    link_id: UUID,
    use_case: Annotated[DeleteIssueLinkUseCase, Depends(get_delete_issue_link_use_case)],
    issue_link_repository: Annotated[IssueLinkRepository, Depends(get_issue_link_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete an issue link."""
    link = await issue_link_repository.get_by_id(link_id)
    if link is None:
        raise HTTPException(status_code=404, detail="Issue link not found")

    issue = await issue_repository.get_by_id(link.source_issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    project = await project_repository.get_by_id(issue.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    await use_case.execute(link_id)
