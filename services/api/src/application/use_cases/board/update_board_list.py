"""Update board list use case."""

from uuid import UUID

import structlog

from src.application.dtos.board import BoardListColumnResponse, UpdateBoardListRequest
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository

logger = structlog.get_logger()


class UpdateBoardListUseCase:
    """Use case for updating a board list (position, list_config)."""

    def __init__(self, board_repository: BoardRepository) -> None:
        self._board_repository = board_repository

    async def execute(
        self,
        list_id: UUID,
        request: UpdateBoardListRequest,
    ) -> BoardListColumnResponse:
        """Update an existing board list."""
        board_list = await self._board_repository.get_board_list_by_id(list_id)
        if board_list is None:
            raise EntityNotFoundException("BoardList", str(list_id))

        if request.position is not None:
            board_list.update_position(request.position)
        if request.list_config is not None:
            board_list.update_list_config(request.list_config)

        updated = await self._board_repository.update_board_list(board_list)
        logger.info("Board list updated", board_list_id=str(list_id))
        return BoardListColumnResponse(
            id=updated.id,
            board_id=updated.board_id,
            list_type=updated.list_type,
            list_config=updated.list_config,
            position=updated.position,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )
