"""Dashboard management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.dashboard import (
    CreateDashboardRequest,
    DashboardListResponse,
    DashboardResponse,
    UpdateDashboardRequest,
    WidgetDataRequest,
    WidgetDataResponse,
)
from src.application.use_cases.dashboard import (
    CreateDashboardUseCase,
    DeleteDashboardUseCase,
    GetDashboardUseCase,
    GetWidgetDataUseCase,
    ListDashboardsUseCase,
    UpdateDashboardUseCase,
)
from src.domain.entities import User
from src.domain.repositories import IssueRepository, ProjectRepository
from src.domain.repositories.dashboard_repository import DashboardRepository
from src.domain.services import PermissionService
from src.infrastructure.database import get_session
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_edit_permission
from src.presentation.dependencies.services import (
    get_dashboard_repository,
    get_issue_repository,
    get_permission_service,
    get_project_repository,
)

router = APIRouter(tags=["Dashboards"])


def get_create_dashboard_use_case(
    dashboard_repository: Annotated[DashboardRepository, Depends(get_dashboard_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> CreateDashboardUseCase:
    """Get create dashboard use case."""
    return CreateDashboardUseCase(dashboard_repository, project_repository)


def get_get_dashboard_use_case(
    dashboard_repository: Annotated[DashboardRepository, Depends(get_dashboard_repository)],
) -> GetDashboardUseCase:
    """Get dashboard use case."""
    return GetDashboardUseCase(dashboard_repository)


def get_list_dashboards_use_case(
    dashboard_repository: Annotated[DashboardRepository, Depends(get_dashboard_repository)],
) -> ListDashboardsUseCase:
    """Get list dashboards use case."""
    return ListDashboardsUseCase(dashboard_repository)


def get_update_dashboard_use_case(
    dashboard_repository: Annotated[DashboardRepository, Depends(get_dashboard_repository)],
) -> UpdateDashboardUseCase:
    """Get update dashboard use case."""
    return UpdateDashboardUseCase(dashboard_repository)


def get_delete_dashboard_use_case(
    dashboard_repository: Annotated[DashboardRepository, Depends(get_dashboard_repository)],
) -> DeleteDashboardUseCase:
    """Get delete dashboard use case."""
    return DeleteDashboardUseCase(dashboard_repository)


def get_get_widget_data_use_case(
    dashboard_repository: Annotated[DashboardRepository, Depends(get_dashboard_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    session: AsyncSession = Depends(get_session),
) -> GetWidgetDataUseCase:
    """Get widget data use case."""
    return GetWidgetDataUseCase(dashboard_repository, issue_repository, project_repository, session)


@router.post(
    "/dashboards",
    response_model=DashboardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create dashboard",
)
async def create_dashboard(
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: CreateDashboardRequest,
    use_case: Annotated[CreateDashboardUseCase, Depends(get_create_dashboard_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> DashboardResponse:
    """Create a new dashboard."""
    if request.project_id:
        project = await project_repository.get_by_id(request.project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        await require_edit_permission(
            project.organization_id,
            current_user,
            permission_service,
            project_id=project.id,
        )

    try:
        return await use_case.execute(current_user.id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/dashboards/{dashboard_id}",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get dashboard",
)
async def get_dashboard(
    current_user: Annotated[User, Depends(get_current_active_user)],
    dashboard_id: UUID,
    use_case: Annotated[GetDashboardUseCase, Depends(get_get_dashboard_use_case)],
    dashboard_repository: Annotated[DashboardRepository, Depends(get_dashboard_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> DashboardResponse:
    """Get dashboard by ID."""
    dashboard = await dashboard_repository.get_by_id(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Check permissions
    if dashboard.user_id != current_user.id:
        if dashboard.project_id:
            project = await project_repository.get_by_id(dashboard.project_id)
            if project:
                await require_edit_permission(
                    project.organization_id,
                    current_user,
                    permission_service,
                    project_id=project.id,
                )
        else:
            raise HTTPException(status_code=403, detail="Access denied")

    return await use_case.execute(dashboard_id)


@router.get(
    "/dashboards",
    response_model=DashboardListResponse,
    status_code=status.HTTP_200_OK,
    summary="List dashboards",
)
async def list_dashboards(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListDashboardsUseCase, Depends(get_list_dashboards_use_case)],
    project_id: Annotated[UUID | None, Query(description="Filter by project ID")] = None,
) -> DashboardListResponse:
    """List dashboards for current user or project."""
    return await use_case.execute(current_user.id, project_id)


@router.put(
    "/dashboards/{dashboard_id}",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Update dashboard",
)
async def update_dashboard(
    current_user: Annotated[User, Depends(get_current_active_user)],
    dashboard_id: UUID,
    request: UpdateDashboardRequest,
    use_case: Annotated[UpdateDashboardUseCase, Depends(get_update_dashboard_use_case)],
    dashboard_repository: Annotated[DashboardRepository, Depends(get_dashboard_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> DashboardResponse:
    """Update a dashboard."""
    dashboard = await dashboard_repository.get_by_id(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Check permissions
    if dashboard.user_id != current_user.id:
        if dashboard.project_id:
            project = await project_repository.get_by_id(dashboard.project_id)
            if project:
                await require_edit_permission(
                    project.organization_id,
                    current_user,
                    permission_service,
                    project_id=project.id,
                )
        else:
            raise HTTPException(status_code=403, detail="Access denied")

    try:
        return await use_case.execute(dashboard_id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete(
    "/dashboards/{dashboard_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete dashboard",
)
async def delete_dashboard(
    current_user: Annotated[User, Depends(get_current_active_user)],
    dashboard_id: UUID,
    use_case: Annotated[DeleteDashboardUseCase, Depends(get_delete_dashboard_use_case)],
    dashboard_repository: Annotated[DashboardRepository, Depends(get_dashboard_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete a dashboard."""
    dashboard = await dashboard_repository.get_by_id(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Check permissions
    if dashboard.user_id != current_user.id:
        if dashboard.project_id:
            project = await project_repository.get_by_id(dashboard.project_id)
            if project:
                await require_edit_permission(
                    project.organization_id,
                    current_user,
                    permission_service,
                    project_id=project.id,
                )
        else:
            raise HTTPException(status_code=403, detail="Access denied")

    await use_case.execute(dashboard_id)


@router.post(
    "/dashboards/{dashboard_id}/widgets/{widget_id}/data",
    response_model=WidgetDataResponse,
    status_code=status.HTTP_200_OK,
    summary="Get widget data",
)
async def get_widget_data(
    current_user: Annotated[User, Depends(get_current_active_user)],
    dashboard_id: UUID,
    widget_id: UUID,
    request: WidgetDataRequest,
    use_case: Annotated[GetWidgetDataUseCase, Depends(get_get_widget_data_use_case)],
    dashboard_repository: Annotated[DashboardRepository, Depends(get_dashboard_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> WidgetDataResponse:
    """Get data for a dashboard widget."""
    dashboard = await dashboard_repository.get_by_id(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Check permissions
    if dashboard.user_id != current_user.id:
        if dashboard.project_id:
            project = await project_repository.get_by_id(dashboard.project_id)
            if project:
                await require_edit_permission(
                    project.organization_id,
                    current_user,
                    permission_service,
                    project_id=project.id,
                )
        else:
            raise HTTPException(status_code=403, detail="Access denied")

    return await use_case.execute(dashboard_id, widget_id, request)
