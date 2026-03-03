"""Set projects for a group board use case."""

from uuid import UUID

import structlog

from src.domain.entities import Board
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import BoardRepository, ProjectRepository

logger = structlog.get_logger()


class SetGroupBoardProjectsUseCase:
    """Use case for replacing the list of projects associated with a group board."""

    def __init__(
        self,
        board_repository: BoardRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._board_repository = board_repository
        self._project_repository = project_repository

    async def execute(
        self,
        board_id: UUID,
        project_ids: list[UUID],
    ) -> Board:
        """Replace ordered list of projects for a group board."""
        logger.info(
            "Setting group board projects",
            board_id=str(board_id),
            project_ids=[str(pid) for pid in project_ids],
        )

        board = await self._board_repository.get_by_id(board_id)
        if board is None:
            raise EntityNotFoundException("Board", str(board_id))
        if board.board_type != "group":
            raise ValidationException("Projects can only be set for group boards")

        if not project_ids:
            raise ValidationException("Group board must include at least one project")

        # Validate projects and ensure they belong to the same organization as the board
        validated_ids: list[UUID] = []
        for project_id in project_ids:
            project = await self._project_repository.get_by_id(project_id)
            if project is None:
                raise EntityNotFoundException("Project", str(project_id))
            if board.organization_id is None or project.organization_id != board.organization_id:
                raise ValidationException(
                    "All projects of a group board must belong to the board organization"
                )
            validated_ids.append(project.id)

        await self._board_repository.set_projects_for_group_board(board_id, validated_ids)
        return board
