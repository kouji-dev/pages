"""Reorder boards use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository, ProjectRepository

logger = structlog.get_logger()


class ReorderBoardsUseCase:
    """Use case for reordering boards within a project."""

    def __init__(
        self,
        board_repository: BoardRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._board_repository = board_repository
        self._project_repository = project_repository

    async def execute(self, project_id: UUID, board_ids: list[UUID]) -> None:
        """Set board order for the project. All board_ids must belong to the project."""
        logger.info(
            "Reordering boards",
            project_id=str(project_id),
            count=len(board_ids),
        )
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            raise EntityNotFoundException("Project", str(project_id))
        for board_id in board_ids:
            board = await self._board_repository.get_by_id(board_id)
            if board is None:
                raise EntityNotFoundException("Board", str(board_id))
            if board.project_id != project_id:
                raise EntityNotFoundException("Board", str(board_id))
        await self._board_repository.reorder_boards(project_id, board_ids)
