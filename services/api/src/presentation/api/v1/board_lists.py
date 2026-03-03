"""Board list (column) API endpoints — update and delete by list ID."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.board import BoardListColumnResponse, UpdateBoardListRequest
from src.application.use_cases.board import DeleteBoardListUseCase, UpdateBoardListUseCase
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository, ProjectRepository
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_edit_permission
from src.presentation.dependencies.services import (
    get_board_repository,
    get_permission_service,
    get_project_repository,
)

router = APIRouter()


def get_update_board_list_use_case(
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
) -> UpdateBoardListUseCase:
    """Update board list use case."""
    return UpdateBoardListUseCase(board_repository)


def get_delete_board_list_use_case(
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
) -> DeleteBoardListUseCase:
    """Delete board list use case."""
    return DeleteBoardListUseCase(board_repository)


@router.put("/{list_id}", response_model=BoardListColumnResponse, status_code=status.HTTP_200_OK)
async def update_board_list(
    current_user: Annotated[User, Depends(get_current_active_user)],
    list_id: UUID,
    request: UpdateBoardListRequest,
    use_case: Annotated[UpdateBoardListUseCase, Depends(get_update_board_list_use_case)],
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> BoardListColumnResponse:
    """Update a board list (position, list_config). Requires edit permission."""
    board_list = await board_repository.get_board_list_by_id(list_id)
    if board_list is None:
        raise HTTPException(status_code=404, detail="Board list not found")
    board = await board_repository.get_by_id(board_list.board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    project = await project_repository.get_by_id(board.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )
    try:
        return await use_case.execute(list_id, request)
    except EntityNotFoundException:
        raise HTTPException(status_code=404, detail="Board list not found") from None


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board_list(
    current_user: Annotated[User, Depends(get_current_active_user)],
    list_id: UUID,
    use_case: Annotated[DeleteBoardListUseCase, Depends(get_delete_board_list_use_case)],
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete a board list (column). Requires edit permission."""
    board_list = await board_repository.get_board_list_by_id(list_id)
    if board_list is None:
        raise HTTPException(status_code=404, detail="Board list not found")
    board = await board_repository.get_by_id(board_list.board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    project = await project_repository.get_by_id(board.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )
    try:
        await use_case.execute(list_id)
    except EntityNotFoundException:
        raise HTTPException(status_code=404, detail="Board list not found") from None
