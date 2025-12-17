"""Time entry management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.time_entry import (
    TimeEntryListResponse,
    TimeEntryRequest,
    TimeEntryResponse,
    TimeSummaryResponse,
)
from src.application.use_cases.time_entry import (
    CreateTimeEntryUseCase,
    DeleteTimeEntryUseCase,
    GetTimeEntryUseCase,
    GetTimeSummaryUseCase,
    ListTimeEntriesUseCase,
    UpdateTimeEntryUseCase,
)
from src.domain.entities import User
from src.domain.repositories import IssueRepository, ProjectRepository
from src.domain.repositories.time_entry_repository import TimeEntryRepository
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_edit_permission
from src.presentation.dependencies.services import (
    get_issue_repository,
    get_permission_service,
    get_project_repository,
    get_time_entry_repository,
)

router = APIRouter(tags=["Time Entries"])


def get_create_time_entry_use_case(
    time_entry_repository: Annotated[TimeEntryRepository, Depends(get_time_entry_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
) -> CreateTimeEntryUseCase:
    """Get create time entry use case."""
    return CreateTimeEntryUseCase(time_entry_repository, issue_repository)


def get_get_time_entry_use_case(
    time_entry_repository: Annotated[TimeEntryRepository, Depends(get_time_entry_repository)],
) -> GetTimeEntryUseCase:
    """Get time entry use case."""
    return GetTimeEntryUseCase(time_entry_repository)


def get_list_time_entries_use_case(
    time_entry_repository: Annotated[TimeEntryRepository, Depends(get_time_entry_repository)],
) -> ListTimeEntriesUseCase:
    """Get list time entries use case."""
    return ListTimeEntriesUseCase(time_entry_repository)


def get_update_time_entry_use_case(
    time_entry_repository: Annotated[TimeEntryRepository, Depends(get_time_entry_repository)],
) -> UpdateTimeEntryUseCase:
    """Get update time entry use case."""
    return UpdateTimeEntryUseCase(time_entry_repository)


def get_delete_time_entry_use_case(
    time_entry_repository: Annotated[TimeEntryRepository, Depends(get_time_entry_repository)],
) -> DeleteTimeEntryUseCase:
    """Get delete time entry use case."""
    return DeleteTimeEntryUseCase(time_entry_repository)


def get_get_time_summary_use_case(
    time_entry_repository: Annotated[TimeEntryRepository, Depends(get_time_entry_repository)],
) -> GetTimeSummaryUseCase:
    """Get time summary use case."""
    return GetTimeSummaryUseCase(time_entry_repository)


@router.post(
    "/issues/{issue_id}/time-entries",
    response_model=TimeEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create time entry",
)
async def create_time_entry(
    current_user: Annotated[User, Depends(get_current_active_user)],
    issue_id: UUID,
    request: TimeEntryRequest,
    use_case: Annotated[CreateTimeEntryUseCase, Depends(get_create_time_entry_use_case)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> TimeEntryResponse:
    """Create a new time entry."""
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
        return await use_case.execute(issue_id, current_user.id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/time-entries/{time_entry_id}",
    response_model=TimeEntryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get time entry",
)
async def get_time_entry(
    current_user: Annotated[User, Depends(get_current_active_user)],
    time_entry_id: UUID,
    use_case: Annotated[GetTimeEntryUseCase, Depends(get_get_time_entry_use_case)],
    time_entry_repository: Annotated[TimeEntryRepository, Depends(get_time_entry_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> TimeEntryResponse:
    """Get time entry by ID."""
    time_entry = await time_entry_repository.get_by_id(time_entry_id)
    if time_entry is None:
        raise HTTPException(status_code=404, detail="Time entry not found")

    issue = await issue_repository.get_by_id(time_entry.issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    project = await project_repository.get_by_id(issue.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    return await use_case.execute(time_entry_id)


@router.get(
    "/issues/{issue_id}/time-entries",
    response_model=TimeEntryListResponse,
    status_code=status.HTTP_200_OK,
    summary="List time entries",
)
async def list_time_entries(
    current_user: Annotated[User, Depends(get_current_active_user)],
    issue_id: UUID,
    use_case: Annotated[ListTimeEntriesUseCase, Depends(get_list_time_entries_use_case)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> TimeEntryListResponse:
    """List all time entries for an issue."""
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


@router.put(
    "/time-entries/{time_entry_id}",
    response_model=TimeEntryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update time entry",
)
async def update_time_entry(
    current_user: Annotated[User, Depends(get_current_active_user)],
    time_entry_id: UUID,
    request: TimeEntryRequest,
    use_case: Annotated[UpdateTimeEntryUseCase, Depends(get_update_time_entry_use_case)],
    time_entry_repository: Annotated[TimeEntryRepository, Depends(get_time_entry_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> TimeEntryResponse:
    """Update a time entry."""
    time_entry = await time_entry_repository.get_by_id(time_entry_id)
    if time_entry is None:
        raise HTTPException(status_code=404, detail="Time entry not found")

    issue = await issue_repository.get_by_id(time_entry.issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    project = await project_repository.get_by_id(issue.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    try:
        return await use_case.execute(time_entry_id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete(
    "/time-entries/{time_entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete time entry",
)
async def delete_time_entry(
    current_user: Annotated[User, Depends(get_current_active_user)],
    time_entry_id: UUID,
    use_case: Annotated[DeleteTimeEntryUseCase, Depends(get_delete_time_entry_use_case)],
    time_entry_repository: Annotated[TimeEntryRepository, Depends(get_time_entry_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete a time entry."""
    time_entry = await time_entry_repository.get_by_id(time_entry_id)
    if time_entry is None:
        raise HTTPException(status_code=404, detail="Time entry not found")

    issue = await issue_repository.get_by_id(time_entry.issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    project = await project_repository.get_by_id(issue.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    await use_case.execute(time_entry_id)


@router.get(
    "/issues/{issue_id}/time-summary",
    response_model=TimeSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get time summary",
)
async def get_time_summary(
    current_user: Annotated[User, Depends(get_current_active_user)],
    issue_id: UUID,
    use_case: Annotated[GetTimeSummaryUseCase, Depends(get_get_time_summary_use_case)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> TimeSummaryResponse:
    """Get time tracking summary for an issue."""
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
