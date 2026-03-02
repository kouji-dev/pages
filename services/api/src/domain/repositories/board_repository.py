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
    ) -> list[Board]:
        """Get boards for a project, ordered by position."""
        ...

    @abstractmethod
    async def count_by_project(self, project_id: UUID) -> int:
        """Count boards in a project."""
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
