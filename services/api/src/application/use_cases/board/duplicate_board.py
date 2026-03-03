"""Duplicate board use case."""

from uuid import UUID

import structlog

from src.application.dtos.board import (
    BoardListColumnResponse,
    BoardWithListsResponse,
)
from src.domain.entities.board import Board, BoardList
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository

logger = structlog.get_logger()

DUPLICATE_NAME_PREFIX = "Copy of "


class DuplicateBoardUseCase:
    """Use case for duplicating a board and its lists."""

    def __init__(self, board_repository: BoardRepository) -> None:
        self._board_repository = board_repository

    async def execute(
        self,
        board_id: UUID,
        created_by: UUID | None = None,
    ) -> BoardWithListsResponse:
        """Duplicate a board: copy configuration and lists with a generated name."""
        logger.info("Duplicating board", board_id=str(board_id))
        result = await self._board_repository.get_by_id_with_lists(board_id)
        if result is None:
            raise EntityNotFoundException("Board", str(board_id))
        board, lists = result
        count = await self._board_repository.count_by_project(board.project_id)
        new_name = f"{DUPLICATE_NAME_PREFIX}{board.name}"
        new_board = Board.create(
            project_id=board.project_id,
            name=new_name,
            description=board.description,
            scope_config=board.scope_config,
            is_default=False,
            position=count,
            created_by=created_by,
        )
        created_board = await self._board_repository.create(new_board)
        created_lists: list[BoardList] = []
        for lst in lists:
            new_list = BoardList.create(
                board_id=created_board.id,
                list_type=lst.list_type,
                list_config=lst.list_config,
                position=lst.position,
            )
            created_list = await self._board_repository.create_board_list(new_list)
            created_lists.append(created_list)
        list_dtos = [
            BoardListColumnResponse(
                id=lst.id,
                board_id=lst.board_id,
                list_type=lst.list_type,
                list_config=lst.list_config,
                position=lst.position,
                created_at=lst.created_at,
                updated_at=lst.updated_at,
            )
            for lst in created_lists
        ]
        return BoardWithListsResponse(
            id=created_board.id,
            project_id=created_board.project_id,
            organization_id=created_board.organization_id,
            board_type=created_board.board_type,
            swimlane_type=created_board.swimlane_type,
            name=created_board.name,
            description=created_board.description,
            scope_config=created_board.scope_config,
            is_default=created_board.is_default,
            position=created_board.position,
            created_by=created_board.created_by,
            created_at=created_board.created_at,
            updated_at=created_board.updated_at,
            lists=list_dtos,
        )
