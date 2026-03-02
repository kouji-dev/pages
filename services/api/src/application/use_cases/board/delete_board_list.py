"""Delete board list use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository

logger = structlog.get_logger()


class DeleteBoardListUseCase:
    """Use case for deleting a board list (column)."""

    def __init__(self, board_repository: BoardRepository) -> None:
        self._board_repository = board_repository

    async def execute(self, list_id: UUID) -> None:
        """Delete a board list."""
        board_list = await self._board_repository.get_board_list_by_id(list_id)
        if board_list is None:
            raise EntityNotFoundException("BoardList", str(list_id))
        await self._board_repository.delete_board_list(list_id)
        logger.info("Board list deleted", board_list_id=str(list_id))
