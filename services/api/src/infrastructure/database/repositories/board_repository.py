"""SQLAlchemy implementation of BoardRepository."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.board import Board, BoardList
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository
from src.infrastructure.database.models import (
    BoardListModel,
    BoardModel,
    GroupBoardProjectModel,
)


class SQLAlchemyBoardRepository(BoardRepository):
    """SQLAlchemy implementation of BoardRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    def _to_entity(self, model: BoardModel) -> Board:
        """Map BoardModel to Board entity."""
        return Board(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            description=model.description,
            scope_config=model.scope_config,
            is_default=model.is_default,
            position=model.position,
            created_by=model.created_by,
            organization_id=model.organization_id,
            board_type=model.board_type,
            swimlane_type=getattr(model, "swimlane_type", "none") or "none",
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _list_to_entity(self, model: BoardListModel) -> BoardList:
        """Map BoardListModel to BoardList entity."""
        return BoardList(
            id=model.id,
            board_id=model.board_id,
            list_type=model.list_type,
            list_config=model.list_config,
            position=model.position,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create(self, board: Board) -> Board:
        """Create a new board."""
        model = BoardModel(
            id=board.id,
            project_id=board.project_id,
            name=board.name,
            description=board.description,
            scope_config=board.scope_config,
            is_default=board.is_default,
            position=board.position,
            created_by=board.created_by,
            organization_id=board.organization_id,
            board_type=board.board_type,
            swimlane_type=board.swimlane_type,
            created_at=board.created_at,
            updated_at=board.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, board_id: UUID) -> Board | None:
        """Get board by ID."""
        result = await self._session.execute(select(BoardModel).where(BoardModel.id == board_id))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def get_by_id_with_lists(self, board_id: UUID) -> tuple[Board, list[BoardList]] | None:
        """Get board by ID with its lists ordered by position."""
        result = await self._session.execute(select(BoardModel).where(BoardModel.id == board_id))
        board_model = result.scalar_one_or_none()
        if board_model is None:
            return None
        lists_result = await self._session.execute(
            select(BoardListModel)
            .where(BoardListModel.board_id == board_id)
            .order_by(BoardListModel.position)
        )
        list_models = lists_result.scalars().all()
        board = self._to_entity(board_model)
        lists = [self._list_to_entity(m) for m in list_models]
        return (board, lists)

    async def get_by_project(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
    ) -> list[Board]:
        """Get boards for a project ordered by position. Optional search by board name."""
        query = (
            select(BoardModel)
            .where(
                BoardModel.project_id == project_id,
                BoardModel.board_type == "project",
            )
            .order_by(BoardModel.position, BoardModel.created_at)
            .offset(skip)
            .limit(limit)
        )
        if search and search.strip():
            pattern = f"%{search.strip()}%"
            query = query.where(BoardModel.name.ilike(pattern))
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def count_by_project(self, project_id: UUID, search: str | None = None) -> int:
        """Count boards in a project. Optional search by board name."""
        query = (
            select(func.count())
            .select_from(BoardModel)
            .where(
                BoardModel.project_id == project_id,
                BoardModel.board_type == "project",
            )
        )
        if search and search.strip():
            pattern = f"%{search.strip()}%"
            query = query.where(BoardModel.name.ilike(pattern))
        result = await self._session.execute(query)
        return int(result.scalar_one())

    async def reorder_boards(self, project_id: UUID, board_ids: list[UUID]) -> None:
        """Set board positions by order of board_ids (index = position)."""
        for position, board_id in enumerate(board_ids):
            result = await self._session.execute(
                select(BoardModel).where(
                    BoardModel.id == board_id,
                    BoardModel.project_id == project_id,
                )
            )
            model = result.scalar_one_or_none()
            if model is not None:
                model.position = position
                model.updated_at = datetime.utcnow()
        await self._session.flush()

    async def update(self, board: Board) -> Board:
        """Update an existing board."""
        result = await self._session.execute(select(BoardModel).where(BoardModel.id == board.id))
        model = result.scalar_one_or_none()
        if model is None:
            raise EntityNotFoundException("Board", str(board.id))
        model.name = board.name
        model.description = board.description
        model.scope_config = board.scope_config
        model.is_default = board.is_default
        model.position = board.position
        model.swimlane_type = board.swimlane_type
        model.updated_at = board.updated_at
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, board_id: UUID) -> None:
        """Delete a board (cascade to board lists)."""
        result = await self._session.execute(select(BoardModel).where(BoardModel.id == board_id))
        model = result.scalar_one_or_none()
        if model is None:
            raise EntityNotFoundException("Board", str(board_id))
        await self._session.delete(model)
        await self._session.flush()

    async def get_lists_for_board(self, board_id: UUID) -> list[BoardList]:
        """Get all lists for a board ordered by position."""
        result = await self._session.execute(
            select(BoardListModel)
            .where(BoardListModel.board_id == board_id)
            .order_by(BoardListModel.position)
        )
        models = result.scalars().all()
        return [self._list_to_entity(m) for m in models]

    async def set_default_board(self, project_id: UUID, board_id: UUID) -> None:
        """Set one board as default and clear others for the project."""
        # Clear all defaults for project
        result = await self._session.execute(
            select(BoardModel).where(BoardModel.project_id == project_id)
        )
        for model in result.scalars().all():
            model.is_default = model.id == board_id
        await self._session.flush()

    async def create_board_list(self, board_list: BoardList) -> BoardList:
        """Create a new board list."""
        model = BoardListModel(
            id=board_list.id,
            board_id=board_list.board_id,
            list_type=board_list.list_type,
            list_config=board_list.list_config,
            position=board_list.position,
            created_at=board_list.created_at,
            updated_at=board_list.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._list_to_entity(model)

    async def get_board_list_by_id(self, list_id: UUID) -> BoardList | None:
        """Get a board list by ID."""
        result = await self._session.execute(
            select(BoardListModel).where(BoardListModel.id == list_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._list_to_entity(model)

    async def update_board_list(self, board_list: BoardList) -> BoardList:
        """Update an existing board list."""
        result = await self._session.execute(
            select(BoardListModel).where(BoardListModel.id == board_list.id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise EntityNotFoundException("BoardList", str(board_list.id))
        model.list_type = board_list.list_type
        model.list_config = board_list.list_config
        model.position = board_list.position
        model.updated_at = board_list.updated_at
        await self._session.flush()
        await self._session.refresh(model)
        return self._list_to_entity(model)

    async def delete_board_list(self, list_id: UUID) -> None:
        """Delete a board list."""
        result = await self._session.execute(
            select(BoardListModel).where(BoardListModel.id == list_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise EntityNotFoundException("BoardList", str(list_id))
        await self._session.delete(model)
        await self._session.flush()

    async def get_max_list_position(self, board_id: UUID) -> int:
        """Get the maximum position among lists for a board (-1 if none)."""
        result = await self._session.execute(
            select(func.coalesce(func.max(BoardListModel.position), -1)).where(
                BoardListModel.board_id == board_id
            )
        )
        return int(result.scalar_one())

    async def get_projects_for_board(self, board_id: UUID) -> list[UUID]:
        """Get project IDs associated to a board ordered by position (group boards)."""
        result = await self._session.execute(
            select(GroupBoardProjectModel)
            .where(GroupBoardProjectModel.group_board_id == board_id)
            .order_by(GroupBoardProjectModel.position, GroupBoardProjectModel.created_at)
        )
        rows = result.scalars().all()
        return [row.project_id for row in rows]

    async def set_projects_for_group_board(self, board_id: UUID, project_ids: list[UUID]) -> None:
        """Replace mapping rows for a group board with given ordered project IDs."""
        # Delete existing mappings
        existing_result = await self._session.execute(
            select(GroupBoardProjectModel).where(
                GroupBoardProjectModel.group_board_id == board_id,
            )
        )
        for row in existing_result.scalars().all():
            await self._session.delete(row)

        # Insert new mappings with explicit positions
        now = datetime.utcnow()
        for position, project_id in enumerate(project_ids):
            mapping = GroupBoardProjectModel(
                group_board_id=board_id,
                project_id=project_id,
                position=position,
                created_at=now,
                updated_at=now,
            )
            self._session.add(mapping)

        await self._session.flush()
