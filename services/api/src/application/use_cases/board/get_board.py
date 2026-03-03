"""Get board use case."""

from uuid import UUID

import structlog

from src.application.dtos.board import (
    BoardListColumnResponse,
    BoardWithListsResponse,
)
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository

logger = structlog.get_logger()


class GetBoardUseCase:
    """Use case for getting a board by ID with its lists."""

    def __init__(self, board_repository: BoardRepository) -> None:
        self._board_repository = board_repository

    async def execute(self, board_id: UUID) -> BoardWithListsResponse:
        """Get board with lists and scope configuration."""
        logger.info("Getting board", board_id=str(board_id))
        result = await self._board_repository.get_by_id_with_lists(board_id)
        if result is None:
            raise EntityNotFoundException("Board", str(board_id))
        board, lists = result
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
        return BoardWithListsResponse(
            id=board.id,
            project_id=board.project_id,
            organization_id=board.organization_id,
            board_type=board.board_type,
            swimlane_type=getattr(board, "swimlane_type", "none"),
            name=board.name,
            description=board.description,
            scope_config=board.scope_config,
            is_default=board.is_default,
            position=board.position,
            created_by=board.created_by,
            created_at=board.created_at,
            updated_at=board.updated_at,
            lists=list_dtos,
        )
