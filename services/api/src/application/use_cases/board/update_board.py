"""Update board use case."""

from uuid import UUID

import structlog

from src.application.dtos.board import BoardResponse, UpdateBoardRequest
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository

logger = structlog.get_logger()


class UpdateBoardUseCase:
    """Use case for updating a board."""

    def __init__(self, board_repository: BoardRepository) -> None:
        self._board_repository = board_repository

    async def execute(
        self,
        board_id: UUID,
        request: UpdateBoardRequest,
    ) -> BoardResponse:
        """Update board name, description, scope_config, position."""
        logger.info("Updating board", board_id=str(board_id))
        board = await self._board_repository.get_by_id(board_id)
        if board is None:
            raise EntityNotFoundException("Board", str(board_id))
        if request.name is not None:
            board.update_name(request.name)
        if request.description is not None:
            board.update_description(request.description)
        if request.scope_config is not None:
            board.update_scope_config(request.scope_config)
        if request.position is not None:
            board.update_position(request.position)
        updated = await self._board_repository.update(board)
        return BoardResponse(
            id=updated.id,
            project_id=updated.project_id,
            organization_id=updated.organization_id,
            board_type=updated.board_type,
            swimlane_type=updated.swimlane_type,
            name=updated.name,
            description=updated.description,
            scope_config=updated.scope_config,
            is_default=updated.is_default,
            position=updated.position,
            created_by=updated.created_by,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )
