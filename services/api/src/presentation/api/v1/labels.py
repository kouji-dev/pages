"""Label API endpoints (global label by ID, update, delete)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.dtos.label import LabelResponse, UpdateLabelRequest
from src.application.use_cases.label import DeleteLabelUseCase, GetLabelUseCase, UpdateLabelUseCase
from src.domain.entities import User
from src.domain.repositories import LabelRepository, ProjectRepository
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_organization_member
from src.presentation.dependencies.services import (
    get_label_repository,
    get_permission_service,
    get_project_repository,
)

router = APIRouter()


def get_get_label_use_case(
    label_repository: Annotated[LabelRepository, Depends(get_label_repository)],
) -> GetLabelUseCase:
    """Get label use case."""
    return GetLabelUseCase(label_repository)


def get_update_label_use_case(
    label_repository: Annotated[LabelRepository, Depends(get_label_repository)],
) -> UpdateLabelUseCase:
    """Update label use case."""
    return UpdateLabelUseCase(label_repository)


def get_delete_label_use_case(
    label_repository: Annotated[LabelRepository, Depends(get_label_repository)],
) -> DeleteLabelUseCase:
    """Delete label use case."""
    return DeleteLabelUseCase(label_repository)


@router.get("/{label_id}", response_model=LabelResponse, status_code=status.HTTP_200_OK)
async def get_label(
    current_user: Annotated[User, Depends(get_current_active_user)],
    label_id: UUID,
    use_case: Annotated[GetLabelUseCase, Depends(get_get_label_use_case)],
    label_repository: Annotated[LabelRepository, Depends(get_label_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> LabelResponse:
    """Get label by ID. Requires project membership."""
    label = await label_repository.get_by_id(label_id)
    if label is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Label not found")
    project = await project_repository.get_by_id(label.project_id)
    if project is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Project not found")
    await require_organization_member(project.organization_id, current_user, permission_service)
    return await use_case.execute(str(label_id))


@router.put("/{label_id}", response_model=LabelResponse, status_code=status.HTTP_200_OK)
async def update_label(
    current_user: Annotated[User, Depends(get_current_active_user)],
    label_id: UUID,
    request: UpdateLabelRequest,
    use_case: Annotated[UpdateLabelUseCase, Depends(get_update_label_use_case)],
    label_repository: Annotated[LabelRepository, Depends(get_label_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> LabelResponse:
    """Update a label. Requires edit permission on project."""
    from fastapi import HTTPException

    from src.presentation.dependencies.permissions import require_edit_permission

    label = await label_repository.get_by_id(label_id)
    if label is None:
        raise HTTPException(status_code=404, detail="Label not found")
    project = await project_repository.get_by_id(label.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )
    return await use_case.execute(str(label_id), request)


@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_label(
    current_user: Annotated[User, Depends(get_current_active_user)],
    label_id: UUID,
    use_case: Annotated[DeleteLabelUseCase, Depends(get_delete_label_use_case)],
    label_repository: Annotated[LabelRepository, Depends(get_label_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete a label. Requires edit permission on project."""
    from fastapi import HTTPException

    from src.presentation.dependencies.permissions import require_edit_permission

    label = await label_repository.get_by_id(label_id)
    if label is None:
        raise HTTPException(status_code=404, detail="Label not found")
    project = await project_repository.get_by_id(label.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )
    await use_case.execute(str(label_id))
