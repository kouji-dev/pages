"""Create board use case."""

from uuid import UUID

import structlog

from src.application.dtos.board import BoardResponse, CreateBoardRequest
from src.domain.entities import Board
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository, ProjectRepository

logger = structlog.get_logger()


class CreateBoardUseCase:
    """Use case for creating a board."""

    def __init__(
        self,
        board_repository: BoardRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._board_repository = board_repository
        self._project_repository = project_repository

    async def execute(
        self,
        project_id: UUID,
        request: CreateBoardRequest,
        created_by: UUID | None = None,
    ) -> BoardResponse:
        """Create a new board in a project. Set as default if first board."""
        logger.info("Creating board", project_id=str(project_id), name=request.name)
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            raise EntityNotFoundException("Project", str(project_id))
        count = await self._board_repository.count_by_project(project_id)
        is_default = request.is_default or (count == 0)
        board = Board.create(
            project_id=project_id,
            name=request.name,
            description=request.description,
            scope_config=request.scope_config,
            is_default=is_default,
            position=request.position,
            created_by=created_by,
        )
        created = await self._board_repository.create(board)
        if is_default and count > 0:
            await self._board_repository.set_default_board(project_id, created.id)
        return BoardResponse(
            id=created.id,
            project_id=created.project_id,
            name=created.name,
            description=created.description,
            scope_config=created.scope_config,
            is_default=created.is_default,
            position=created.position,
            created_by=created.created_by,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )
