"""Create board list (column) use case."""

from uuid import UUID

import structlog

from src.application.dtos.board import BoardListColumnResponse, CreateBoardListRequest
from src.domain.entities.board import BoardList
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository

logger = structlog.get_logger()


class CreateBoardListUseCase:
    """Use case for creating a board list (column)."""

    def __init__(self, board_repository: BoardRepository) -> None:
        self._board_repository = board_repository

    async def execute(
        self,
        board_id: UUID,
        request: CreateBoardListRequest,
    ) -> BoardListColumnResponse:
        """Create a new board list. Position is set to max+1."""
        board = await self._board_repository.get_by_id(board_id)
        if board is None:
            raise EntityNotFoundException("Board", str(board_id))

        max_pos = await self._board_repository.get_max_list_position(board_id)
        position = max_pos + 1

        board_list = BoardList.create(
            board_id=board_id,
            list_type=request.list_type,
            list_config=request.list_config,
            position=position,
        )
        created = await self._board_repository.create_board_list(board_list)
        logger.info(
            "Board list created",
            board_list_id=str(created.id),
            board_id=str(board_id),
            list_type=created.list_type,
        )
        return BoardListColumnResponse(
            id=created.id,
            board_id=created.board_id,
            list_type=created.list_type,
            list_config=created.list_config,
            position=created.position,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )
