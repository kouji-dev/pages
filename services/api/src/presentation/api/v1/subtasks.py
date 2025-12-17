"""Subtask management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.issue import IssueListItemResponse
from src.application.use_cases.subtask import ListSubtasksUseCase
from src.domain.entities import User
from src.domain.repositories import IssueRepository, ProjectRepository
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_edit_permission
from src.presentation.dependencies.services import (
    get_issue_repository,
    get_permission_service,
    get_project_repository,
)

router = APIRouter(tags=["Subtasks"])


def get_list_subtasks_use_case(
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
) -> ListSubtasksUseCase:
    """Get list subtasks use case."""
    return ListSubtasksUseCase(issue_repository)


@router.get(
    "/issues/{issue_id}/subtasks",
    response_model=list[IssueListItemResponse],
    status_code=status.HTTP_200_OK,
    summary="List subtasks",
)
async def list_subtasks(
    current_user: Annotated[User, Depends(get_current_active_user)],
    issue_id: UUID,
    use_case: Annotated[ListSubtasksUseCase, Depends(get_list_subtasks_use_case)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> list[IssueListItemResponse]:
    """List all subtasks for an issue."""
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
