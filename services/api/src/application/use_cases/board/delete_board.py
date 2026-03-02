"""Delete board use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import BoardRepository

logger = structlog.get_logger()


class DeleteBoardUseCase:
    """Use case for deleting a board. Prevents deletion of last board."""

    def __init__(self, board_repository: BoardRepository) -> None:
        self._board_repository = board_repository

    async def execute(self, board_id: UUID) -> None:
        """Delete a board. Cascade to board lists. Prevent delete if last board."""
        logger.info("Deleting board", board_id=str(board_id))
        board = await self._board_repository.get_by_id(board_id)
        if board is None:
            raise EntityNotFoundException("Board", str(board_id))
        count = await self._board_repository.count_by_project(board.project_id)
        if count <= 1:
            raise ConflictException(
                "Cannot delete the last board of a project. Create another board first."
            )
        await self._board_repository.delete(board_id)
