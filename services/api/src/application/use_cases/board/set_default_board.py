"""Set default board use case."""

from uuid import UUID

import structlog

from src.application.dtos.board import BoardResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository, ProjectRepository

logger = structlog.get_logger()


class SetDefaultBoardUseCase:
    """Use case for setting a board as the project default."""

    def __init__(
        self,
        board_repository: BoardRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._board_repository = board_repository
        self._project_repository = project_repository

    async def execute(self, board_id: UUID) -> BoardResponse:
        """Set the board as default for its project. Unsets previous default."""
        logger.info("Setting default board", board_id=str(board_id))
        board = await self._board_repository.get_by_id(board_id)
        if board is None:
            raise EntityNotFoundException("Board", str(board_id))
        project = await self._project_repository.get_by_id(board.project_id)
        if project is None:
            raise EntityNotFoundException("Project", str(board.project_id))
        await self._board_repository.set_default_board(board.project_id, board_id)
        updated = await self._board_repository.get_by_id(board_id)
        if updated is None:
            raise EntityNotFoundException("Board", str(board_id))
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
