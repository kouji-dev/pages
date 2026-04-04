"""Remove one project from a group board use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import BoardRepository

logger = structlog.get_logger()


class RemoveGroupBoardProjectUseCase:
    """Use case for removing a single project association from a group board."""

    def __init__(self, board_repository: BoardRepository) -> None:
        self._board_repository = board_repository

    async def execute(self, board_id: UUID, project_id: UUID) -> None:
        """Remove project_id from the group board's project list."""
        logger.info(
            "Removing project from group board",
            board_id=str(board_id),
            project_id=str(project_id),
        )

        board = await self._board_repository.get_by_id(board_id)
        if board is None:
            raise EntityNotFoundException("Board", str(board_id))
        if board.board_type != "group":
            raise ValidationException("Projects can only be removed from group boards")

        linked = await self._board_repository.get_projects_for_board(board_id)
        if project_id not in linked:
            raise ValidationException("Project is not linked to this group board")
        if len(linked) <= 1:
            raise ValidationException("Group board must include at least one project")

        await self._board_repository.remove_project_from_group_board(board_id, project_id)
