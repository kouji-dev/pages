"""Macro repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Macro


class MacroRepository(ABC):
    """Abstract macro repository interface."""

    @abstractmethod
    async def create(self, macro: Macro) -> Macro:
        """Create a new macro.

        Args:
            macro: Macro entity to create

        Returns:
            Created macro with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, macro_id: UUID) -> Macro | None:
        """Get macro by ID.

        Args:
            macro_id: Macro UUID

        Returns:
            Macro if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Macro | None:
        """Get macro by name.

        Args:
            name: Macro name

        Returns:
            Macro if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        macro_type: str | None = None,
        include_system: bool = True,
    ) -> list[Macro]:
        """Get all macros with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            macro_type: Optional macro type filter
            include_system: Whether to include system macros

        Returns:
            List of macros
        """
        ...

    @abstractmethod
    async def count(
        self,
        macro_type: str | None = None,
        include_system: bool = True,
    ) -> int:
        """Count total macros.

        Args:
            macro_type: Optional macro type filter
            include_system: Whether to include system macros

        Returns:
            Total count of macros
        """
        ...

    @abstractmethod
    async def update(self, macro: Macro) -> Macro:
        """Update an existing macro.

        Args:
            macro: Macro entity with updated data

        Returns:
            Updated macro

        Raises:
            EntityNotFoundException: If macro not found
        """
        ...

    @abstractmethod
    async def delete(self, macro_id: UUID) -> None:
        """Delete a macro.

        Args:
            macro_id: Macro UUID

        Raises:
            EntityNotFoundException: If macro not found
            ValueError: If trying to delete a system macro
        """
        ...
