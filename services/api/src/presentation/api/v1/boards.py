"""Board API endpoints (get, update, delete by board ID; lists; issues)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.board import (
    BoardIssueItemResponse,
    BoardIssuesResponse,
    BoardListColumnListResponse,
    BoardListColumnResponse,
    BoardResponse,
    BoardWithListsResponse,
    CreateBoardListRequest,
    MoveBoardIssueRequest,
    UpdateBoardRequest,
)
from src.application.use_cases.board import (
    CreateBoardListUseCase,
    DeleteBoardListUseCase,
    DeleteBoardUseCase,
    GetBoardIssuesUseCase,
    GetBoardUseCase,
    ListBoardListsUseCase,
    MoveBoardIssueUseCase,
    UpdateBoardListUseCase,
    UpdateBoardUseCase,
)
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    BoardRepository,
    CommentRepository,
    IssueActivityRepository,
    IssueRepository,
    LabelRepository,
    ProjectRepository,
    SprintRepository,
)
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import (
    require_edit_permission,
    require_organization_member,
)
from src.presentation.dependencies.services import (
    get_board_repository,
    get_comment_repository,
    get_issue_activity_repository,
    get_issue_repository,
    get_label_repository,
    get_permission_service,
    get_project_repository,
    get_sprint_repository,
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


def get_create_board_list_use_case(
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
) -> CreateBoardListUseCase:
    """Create board list use case."""
    return CreateBoardListUseCase(board_repository)


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


def get_list_board_lists_use_case(
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
) -> ListBoardListsUseCase:
    """List board lists use case."""
    return ListBoardListsUseCase(board_repository)


def get_get_board_issues_use_case(
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    label_repository: Annotated[LabelRepository, Depends(get_label_repository)],
    comment_repository: Annotated[CommentRepository, Depends(get_comment_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> GetBoardIssuesUseCase:
    """Get board issues use case."""
    return GetBoardIssuesUseCase(
        board_repository,
        issue_repository,
        label_repository,
        comment_repository,
        project_repository,
    )


def get_move_board_issue_use_case(
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    label_repository: Annotated[LabelRepository, Depends(get_label_repository)],
    sprint_repository: Annotated[SprintRepository, Depends(get_sprint_repository)],
    comment_repository: Annotated[CommentRepository, Depends(get_comment_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    issue_activity_repository: Annotated[
        IssueActivityRepository, Depends(get_issue_activity_repository)
    ],
) -> MoveBoardIssueUseCase:
    """Move board issue use case."""
    return MoveBoardIssueUseCase(
        board_repository,
        issue_repository,
        label_repository,
        sprint_repository,
        comment_repository,
        project_repository,
        issue_activity_repository,
    )


@router.post(
    "/{board_id}/lists",
    response_model=BoardListColumnResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_board_list(
    current_user: Annotated[User, Depends(get_current_active_user)],
    board_id: UUID,
    request: CreateBoardListRequest,
    use_case: Annotated[CreateBoardListUseCase, Depends(get_create_board_list_use_case)],
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> BoardListColumnResponse:
    """Create a board list (column). Position = end. Requires edit permission."""
    board = await board_repository.get_by_id(board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    project = await project_repository.get_by_id(board.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )
    try:
        return await use_case.execute(board_id, request)
    except EntityNotFoundException:
        raise HTTPException(status_code=404, detail="Board not found") from None


@router.get(
    "/{board_id}/lists",
    response_model=BoardListColumnListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_board_lists(
    current_user: Annotated[User, Depends(get_current_active_user)],
    board_id: UUID,
    use_case: Annotated[ListBoardListsUseCase, Depends(get_list_board_lists_use_case)],
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> BoardListColumnListResponse:
    """List board lists (columns) ordered by position. Requires project membership."""
    board = await board_repository.get_by_id(board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    project = await project_repository.get_by_id(board.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await require_organization_member(project.organization_id, current_user, permission_service)
    try:
        return await use_case.execute(board_id)
    except EntityNotFoundException:
        raise HTTPException(status_code=404, detail="Board not found") from None


@router.get(
    "/{board_id}/issues",
    response_model=BoardIssuesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_board_issues(
    current_user: Annotated[User, Depends(get_current_active_user)],
    board_id: UUID,
    use_case: Annotated[GetBoardIssuesUseCase, Depends(get_get_board_issues_use_case)],
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> BoardIssuesResponse:
    """Get board issues grouped by list (scope applied). Requires project membership."""
    board = await board_repository.get_by_id(board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    project = await project_repository.get_by_id(board.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await require_organization_member(project.organization_id, current_user, permission_service)
    try:
        return await use_case.execute(board_id)
    except EntityNotFoundException:
        raise HTTPException(status_code=404, detail="Board not found") from None


@router.put(
    "/{board_id}/issues/{issue_id}/move",
    response_model=BoardIssueItemResponse,
    status_code=status.HTTP_200_OK,
)
async def move_board_issue(
    current_user: Annotated[User, Depends(get_current_active_user)],
    board_id: UUID,
    issue_id: UUID,
    request: MoveBoardIssueRequest,
    use_case: Annotated[MoveBoardIssueUseCase, Depends(get_move_board_issue_use_case)],
    board_repository: Annotated[BoardRepository, Depends(get_board_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> BoardIssueItemResponse:
    """Move an issue between board lists (drag & drop with label/assignee/milestone swapping). Requires edit permission."""
    board = await board_repository.get_by_id(board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    project = await project_repository.get_by_id(board.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )
    try:
        return await use_case.execute(
            board_id=board_id,
            issue_id=issue_id,
            source_list_id=request.source_list_id,
            target_list_id=request.target_list_id,
            user_id=current_user.id,
        )
    except EntityNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message) from e


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
