"""Custom field management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.custom_field import (
    CustomFieldListResponse,
    CustomFieldRequest,
    CustomFieldResponse,
    UpdateCustomFieldRequest,
)
from src.application.use_cases.custom_field import (
    CreateCustomFieldUseCase,
    DeleteCustomFieldUseCase,
    GetCustomFieldUseCase,
    ListCustomFieldsUseCase,
    UpdateCustomFieldUseCase,
)
from src.domain.entities import User
from src.domain.repositories import ProjectRepository
from src.domain.repositories.custom_field_repository import CustomFieldRepository
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_edit_permission
from src.presentation.dependencies.services import (
    get_custom_field_repository,
    get_permission_service,
    get_project_repository,
)

router = APIRouter(tags=["Custom Fields"])


def get_create_custom_field_use_case(
    custom_field_repository: Annotated[CustomFieldRepository, Depends(get_custom_field_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> CreateCustomFieldUseCase:
    """Get create custom field use case."""
    return CreateCustomFieldUseCase(custom_field_repository, project_repository)


def get_get_custom_field_use_case(
    custom_field_repository: Annotated[CustomFieldRepository, Depends(get_custom_field_repository)],
) -> GetCustomFieldUseCase:
    """Get custom field use case."""
    return GetCustomFieldUseCase(custom_field_repository)


def get_list_custom_fields_use_case(
    custom_field_repository: Annotated[CustomFieldRepository, Depends(get_custom_field_repository)],
) -> ListCustomFieldsUseCase:
    """Get list custom fields use case."""
    return ListCustomFieldsUseCase(custom_field_repository)


def get_update_custom_field_use_case(
    custom_field_repository: Annotated[CustomFieldRepository, Depends(get_custom_field_repository)],
) -> UpdateCustomFieldUseCase:
    """Get update custom field use case."""
    return UpdateCustomFieldUseCase(custom_field_repository)


def get_delete_custom_field_use_case(
    custom_field_repository: Annotated[CustomFieldRepository, Depends(get_custom_field_repository)],
) -> DeleteCustomFieldUseCase:
    """Get delete custom field use case."""
    return DeleteCustomFieldUseCase(custom_field_repository)


@router.post(
    "/projects/{project_id}/custom-fields",
    response_model=CustomFieldResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create custom field",
)
async def create_custom_field(
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_id: UUID,
    request: CustomFieldRequest,
    use_case: Annotated[CreateCustomFieldUseCase, Depends(get_create_custom_field_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> CustomFieldResponse:
    """Create a new custom field."""
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
    "/custom-fields/{custom_field_id}",
    response_model=CustomFieldResponse,
    status_code=status.HTTP_200_OK,
    summary="Get custom field",
)
async def get_custom_field(
    current_user: Annotated[User, Depends(get_current_active_user)],
    custom_field_id: UUID,
    use_case: Annotated[GetCustomFieldUseCase, Depends(get_get_custom_field_use_case)],
    custom_field_repository: Annotated[CustomFieldRepository, Depends(get_custom_field_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> CustomFieldResponse:
    """Get custom field by ID."""
    custom_field = await custom_field_repository.get_by_id(custom_field_id)
    if custom_field is None:
        raise HTTPException(status_code=404, detail="Custom field not found")

    project = await project_repository.get_by_id(custom_field.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    return await use_case.execute(custom_field_id)


@router.get(
    "/projects/{project_id}/custom-fields",
    response_model=CustomFieldListResponse,
    status_code=status.HTTP_200_OK,
    summary="List custom fields",
)
async def list_custom_fields(
    current_user: Annotated[User, Depends(get_current_active_user)],
    project_id: UUID,
    use_case: Annotated[ListCustomFieldsUseCase, Depends(get_list_custom_fields_use_case)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> CustomFieldListResponse:
    """List all custom fields for a project."""
    project = await project_repository.get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    return await use_case.execute(project_id)


@router.put(
    "/custom-fields/{custom_field_id}",
    response_model=CustomFieldResponse,
    status_code=status.HTTP_200_OK,
    summary="Update custom field",
)
async def update_custom_field(
    current_user: Annotated[User, Depends(get_current_active_user)],
    custom_field_id: UUID,
    request: UpdateCustomFieldRequest,
    use_case: Annotated[UpdateCustomFieldUseCase, Depends(get_update_custom_field_use_case)],
    custom_field_repository: Annotated[CustomFieldRepository, Depends(get_custom_field_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> CustomFieldResponse:
    """Update a custom field."""
    custom_field = await custom_field_repository.get_by_id(custom_field_id)
    if custom_field is None:
        raise HTTPException(status_code=404, detail="Custom field not found")

    project = await project_repository.get_by_id(custom_field.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    try:
        return await use_case.execute(custom_field_id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete(
    "/custom-fields/{custom_field_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete custom field",
)
async def delete_custom_field(
    current_user: Annotated[User, Depends(get_current_active_user)],
    custom_field_id: UUID,
    use_case: Annotated[DeleteCustomFieldUseCase, Depends(get_delete_custom_field_use_case)],
    custom_field_repository: Annotated[CustomFieldRepository, Depends(get_custom_field_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete a custom field."""
    custom_field = await custom_field_repository.get_by_id(custom_field_id)
    if custom_field is None:
        raise HTTPException(status_code=404, detail="Custom field not found")

    project = await project_repository.get_by_id(custom_field.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    await use_case.execute(custom_field_id)
