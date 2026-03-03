"""List board lists (columns) use case."""

from uuid import UUID

import structlog

from src.application.dtos.board import BoardListColumnListResponse, BoardListColumnResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository

logger = structlog.get_logger()


class ListBoardListsUseCase:
    """Use case for listing board lists (columns) ordered by position."""

    def __init__(self, board_repository: BoardRepository) -> None:
        self._board_repository = board_repository

    async def execute(self, board_id: UUID) -> BoardListColumnListResponse:
        """List all lists for a board, ordered by position."""
        board = await self._board_repository.get_by_id(board_id)
        if board is None:
            raise EntityNotFoundException("Board", str(board_id))
        lists = await self._board_repository.get_lists_for_board(board_id)
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
            for lst in lists
        ]
        return BoardListColumnListResponse(lists=list_dtos, total=len(list_dtos))
