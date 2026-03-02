"""List project boards use case."""

from uuid import UUID

import structlog

from src.application.dtos.board import BoardListItemResponse, BoardListResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository, ProjectRepository

logger = structlog.get_logger()


class ListProjectBoardsUseCase:
    """Use case for listing boards in a project."""

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
        page: int = 1,
        limit: int = 20,
    ) -> BoardListResponse:
        """List boards for a project, sorted by position."""
        logger.info("Listing boards", project_id=str(project_id), page=page, limit=limit)
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            raise EntityNotFoundException("Project", str(project_id))
        skip = (page - 1) * limit
        boards = await self._board_repository.get_by_project(
            project_id=project_id,
            skip=skip,
            limit=limit,
        )
        total = await self._board_repository.count_by_project(project_id)
        pages = (total + limit - 1) // limit if total > 0 else 0
        items = [
            BoardListItemResponse(
                id=b.id,
                project_id=b.project_id,
                name=b.name,
                description=b.description,
                scope_config=b.scope_config,
                is_default=b.is_default,
                position=b.position,
                created_by=b.created_by,
                created_at=b.created_at,
                updated_at=b.updated_at,
            )
            for b in boards
        ]
        return BoardListResponse(
            boards=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )
