"""Board API endpoints (get, update, delete by board ID)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.board import BoardResponse, BoardWithListsResponse, UpdateBoardRequest
from src.application.use_cases.board import (
    DeleteBoardUseCase,
    GetBoardUseCase,
    UpdateBoardUseCase,
)
from src.domain.entities import User
from src.domain.repositories import BoardRepository, ProjectRepository
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import (
    require_edit_permission,
    require_organization_member,
)
from src.presentation.dependencies.services import (
    get_board_repository,
    get_permission_service,
    get_project_repository,
)

router = APIRouter()


def get_get_board_use_case(
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
) -> GetBoardUseCase:
    """Get board use case."""
    return GetBoardUseCase(board_repository)


def get_update_board_use_case(
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
) -> UpdateBoardUseCase:
    """Update board use case."""
    return UpdateBoardUseCase(board_repository)


def get_delete_board_use_case(
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
) -> DeleteBoardUseCase:
    """Delete board use case."""
    return DeleteBoardUseCase(board_repository)


@router.get("/{board_id}", response_model=BoardWithListsResponse, status_code=status.HTTP_200_OK)
async def get_board(
    current_user: Annotated[User, Depends(get_current_active_user)],
    board_id: UUID,
    use_case: Annotated[GetBoardUseCase, Depends(get_get_board_use_case)],
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> BoardWithListsResponse:
    """Get board by ID with lists and scope config. Requires project membership."""
    board = await board_repository.get_by_id(board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    project = await project_repository.get_by_id(board.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await require_organization_member(project.organization_id, current_user, permission_service)
    return await use_case.execute(board_id)


@router.put("/{board_id}", response_model=BoardResponse, status_code=status.HTTP_200_OK)
async def update_board(
    current_user: Annotated[User, Depends(get_current_active_user)],
    board_id: UUID,
    request: UpdateBoardRequest,
    use_case: Annotated[UpdateBoardUseCase, Depends(get_update_board_use_case)],
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> BoardResponse:
    """Update a board (name, description, scope_config, position). Requires edit permission."""
    board = await board_repository.get_by_id(board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    project = await project_repository.get_by_id(board.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )
    return await use_case.execute(board_id, request)


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    current_user: Annotated[User, Depends(get_current_active_user)],
    board_id: UUID,
    use_case: Annotated[DeleteBoardUseCase, Depends(get_delete_board_use_case)],
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete a board. Cascade to lists. Cannot delete last board. Requires edit permission."""
    board = await board_repository.get_by_id(board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    project = await project_repository.get_by_id(board.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )
    await use_case.execute(board_id)
