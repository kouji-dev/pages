"""Board repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.board import Board, BoardList


class BoardRepository(ABC):
    """Abstract board repository interface."""

    @abstractmethod
    async def create(self, board: Board) -> Board:
        """Create a new board.

        Args:
            board: Board entity to create

        Returns:
            Created board with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, board_id: UUID) -> Board | None:
        """Get board by ID (without lists)."""
        ...

    @abstractmethod
    async def get_by_id_with_lists(self, board_id: UUID) -> tuple[Board, list[BoardList]] | None:
        """Get board by ID including its lists ordered by position."""
        ...

    @abstractmethod
    async def get_by_project(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
    ) -> list[Board]:
        """Get boards for a project, ordered by position. Optional search by board name."""
        ...

    @abstractmethod
    async def count_by_project(self, project_id: UUID, search: str | None = None) -> int:
        """Count boards in a project. Optional search by board name."""
        ...

    @abstractmethod
    async def reorder_boards(self, project_id: UUID, board_ids: list[UUID]) -> None:
        """Set board positions by order of board_ids (index = position)."""
        ...

    @abstractmethod
    async def update(self, board: Board) -> Board:
        """Update an existing board."""
        ...

    @abstractmethod
    async def delete(self, board_id: UUID) -> None:
        """Delete a board (cascade to board lists)."""
        ...

    @abstractmethod
    async def get_lists_for_board(self, board_id: UUID) -> list[BoardList]:
        """Get all lists for a board, ordered by position."""
        ...

    @abstractmethod
    async def set_default_board(self, project_id: UUID, board_id: UUID) -> None:
        """Set one board as default and clear others for the project."""
        ...

    @abstractmethod
    async def create_board_list(self, board_list: BoardList) -> BoardList:
        """Create a new board list (column)."""
        ...

    @abstractmethod
    async def get_board_list_by_id(self, list_id: UUID) -> BoardList | None:
        """Get a board list by ID."""
        ...

    @abstractmethod
    async def update_board_list(self, board_list: BoardList) -> BoardList:
        """Update an existing board list."""
        ...

    @abstractmethod
    async def delete_board_list(self, list_id: UUID) -> None:
        """Delete a board list."""
        ...

    @abstractmethod
    async def get_max_list_position(self, board_id: UUID) -> int:
        """Get the maximum position among lists for a board (-1 if none)."""
        ...

    # --- Group boards (organization-level boards spanning multiple projects) ---

    @abstractmethod
    async def get_projects_for_board(self, board_id: UUID) -> list[UUID]:
        """Get project IDs associated to a board (for group boards this is the full mapping)."""
        ...

    @abstractmethod
    async def set_projects_for_group_board(self, board_id: UUID, project_ids: list[UUID]) -> None:
        """Replace the list of projects associated to a group board, preserving order as given."""
        ...
