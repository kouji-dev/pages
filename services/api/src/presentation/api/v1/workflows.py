"""Workflow management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.workflow import (
    CreateWorkflowRequest,
    UpdateWorkflowRequest,
    ValidateTransitionRequest,
    ValidateTransitionResponse,
    WorkflowListResponse,
    WorkflowResponse,
)
from src.application.use_cases.workflow import (
    CreateWorkflowUseCase,
    DeleteWorkflowUseCase,
    GetWorkflowUseCase,
    ListWorkflowsUseCase,
    UpdateWorkflowUseCase,
    ValidateTransitionUseCase,
)
from src.domain.entities import User
from src.domain.repositories import ProjectRepository, WorkflowRepository
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_edit_permission
from src.presentation.dependencies.services import (
    get_permission_service,
    get_project_repository,
    get_workflow_repository,
)

router = APIRouter(tags=["Workflows"])


# Dependency injection for use cases
def get_create_workflow_use_case(
    workflow_repository: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> CreateWorkflowUseCase:
    """Get create workflow use case with dependencies."""
    return CreateWorkflowUseCase(workflow_repository, project_repository)


def get_get_workflow_use_case(
    workflow_repository: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
) -> GetWorkflowUseCase:
    """Get workflow use case with dependencies."""
    return GetWorkflowUseCase(workflow_repository)


def get_list_workflows_use_case(
    workflow_repository: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
) -> ListWorkflowsUseCase:
    """Get list workflows use case with dependencies."""
    return ListWorkflowsUseCase(workflow_repository)


def get_update_workflow_use_case(
    workflow_repository: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
) -> UpdateWorkflowUseCase:
    """Get update workflow use case with dependencies."""
    return UpdateWorkflowUseCase(workflow_repository)


def get_delete_workflow_use_case(
    workflow_repository: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
) -> DeleteWorkflowUseCase:
    """Get delete workflow use case with dependencies."""
    return DeleteWorkflowUseCase(workflow_repository)


def get_validate_transition_use_case(
    workflow_repository: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
) -> ValidateTransitionUseCase:
    """Get validate transition use case with dependencies."""
    return ValidateTransitionUseCase(workflow_repository)


@router.post(
    "/projects/{project_id}/workflows",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create workflow",
    description="Create a new workflow for a project",
)
async def create_workflow(
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_id: UUID,
    request: CreateWorkflowRequest,
    use_case: Annotated[CreateWorkflowUseCase, Depends(get_create_workflow_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> WorkflowResponse:
    """Create a new workflow.

    Requires project edit permissions.
    """
    # Check user has edit permissions
    project = await project_repository.get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    try:
        return await use_case.execute(project_id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/workflows/{workflow_id}",
    response_model=WorkflowResponse,
    status_code=status.HTTP_200_OK,
    summary="Get workflow",
    description="Get workflow by ID",
)
async def get_workflow(
    current_user: Annotated[User, Depends(get_current_active_user)],
    workflow_id: UUID,
    use_case: Annotated[GetWorkflowUseCase, Depends(get_get_workflow_use_case)],
    workflow_repository: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> WorkflowResponse:
    """Get workflow by ID.

    Requires project membership.
    """
    # Get workflow to check project
    workflow = await workflow_repository.get_by_id(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Check user has project membership
    project = await project_repository.get_by_id(workflow.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    return await use_case.execute(workflow_id)


@router.get(
    "/projects/{project_id}/workflows",
    response_model=WorkflowListResponse,
    status_code=status.HTTP_200_OK,
    summary="List workflows",
    description="List all workflows for a project",
)
async def list_workflows(
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_id: UUID,
    use_case: Annotated[ListWorkflowsUseCase, Depends(get_list_workflows_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> WorkflowListResponse:
    """List all workflows for a project.

    Requires project membership.
    """
    # Check user has project membership
    project = await project_repository.get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    return await use_case.execute(project_id)


@router.put(
    "/workflows/{workflow_id}",
    response_model=WorkflowResponse,
    status_code=status.HTTP_200_OK,
    summary="Update workflow",
    description="Update a workflow",
)
async def update_workflow(
    current_user: Annotated[User, Depends(get_current_active_user)],
    workflow_id: UUID,
    request: UpdateWorkflowRequest,
    use_case: Annotated[UpdateWorkflowUseCase, Depends(get_update_workflow_use_case)],
    workflow_repository: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> WorkflowResponse:
    """Update a workflow.

    Requires project edit permissions.
    """
    # Get workflow to check project
    workflow = await workflow_repository.get_by_id(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Check user has edit permissions
    project = await project_repository.get_by_id(workflow.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    try:
        return await use_case.execute(workflow_id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete(
    "/workflows/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workflow",
    description="Delete a workflow",
)
async def delete_workflow(
    current_user: Annotated[User, Depends(get_current_active_user)],
    workflow_id: UUID,
    use_case: Annotated[DeleteWorkflowUseCase, Depends(get_delete_workflow_use_case)],
    workflow_repository: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete a workflow.

    Requires project edit permissions.
    """
    # Get workflow to check project
    workflow = await workflow_repository.get_by_id(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Check user has edit permissions
    project = await project_repository.get_by_id(workflow.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    await use_case.execute(workflow_id)


@router.post(
    "/workflows/{workflow_id}/validate-transition",
    response_model=ValidateTransitionResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate transition",
    description="Validate if a transition is allowed in a workflow",
)
async def validate_transition(
    current_user: Annotated[User, Depends(get_current_active_user)],
    workflow_id: UUID,
    request: ValidateTransitionRequest,
    use_case: Annotated[ValidateTransitionUseCase, Depends(get_validate_transition_use_case)],
    workflow_repository: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> ValidateTransitionResponse:
    """Validate if a transition is allowed in a workflow.

    Requires project membership.
    """
    # Get workflow to check project
    workflow = await workflow_repository.get_by_id(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Check user has project membership
    project = await project_repository.get_by_id(workflow.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    return await use_case.execute(workflow_id, request)
