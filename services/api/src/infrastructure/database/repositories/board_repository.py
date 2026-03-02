"""SQLAlchemy implementation of BoardRepository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.board import Board, BoardList
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import BoardRepository
from src.infrastructure.database.models import BoardListModel, BoardModel


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
    ) -> list[Board]:
        """Get boards for a project ordered by position."""
        query = (
            select(BoardModel)
            .where(BoardModel.project_id == project_id)
            .order_by(BoardModel.position, BoardModel.created_at)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def count_by_project(self, project_id: UUID) -> int:
        """Count boards in a project."""
        query = (
            select(func.count()).select_from(BoardModel).where(BoardModel.project_id == project_id)
        )
        result = await self._session.execute(query)
        return int(result.scalar_one())

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
        from sqlalchemy import func

        result = await self._session.execute(
            select(func.coalesce(func.max(BoardListModel.position), -1)).where(
                BoardListModel.board_id == board_id
            )
        )
        return int(result.scalar_one())
