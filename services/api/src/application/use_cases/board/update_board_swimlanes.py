"""Update board swimlane type use case."""

from __future__ import annotations

from uuid import UUID

from src.domain.entities.board import Board
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository


class UpdateBoardSwimlanesUseCase:
    """Use case for PUT /boards/:id/swimlanes — update board swimlane type."""

    def __init__(self, board_repository: BoardRepository) -> None:
        self._board_repository = board_repository

    async def execute(self, board_id: UUID, swimlane_type: str) -> Board:
        """Update board swimlane type to 'none', 'epic', or 'assignee'."""
        board = await self._board_repository.get_by_id(board_id)
        if board is None:
            raise EntityNotFoundException("Board", str(board_id))
        board.update_swimlane_type(swimlane_type)
        return await self._board_repository.update(board)
