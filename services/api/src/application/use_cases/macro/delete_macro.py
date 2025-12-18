"""Delete macro use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import MacroRepository

logger = structlog.get_logger()


class DeleteMacroUseCase:
    """Use case for deleting a macro."""

    def __init__(self, macro_repository: MacroRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            macro_repository: Macro repository
        """
        self._macro_repository = macro_repository

    async def execute(self, macro_id: str) -> None:
        """Execute delete macro.

        Args:
            macro_id: Macro ID

        Raises:
            EntityNotFoundException: If macro not found
            ValueError: If trying to delete a system macro
        """
        logger.info("Deleting macro", macro_id=macro_id)

        macro_uuid = UUID(macro_id)
        macro = await self._macro_repository.get_by_id(macro_uuid)

        if macro is None:
            logger.warning("Macro not found for deletion", macro_id=macro_id)
            raise EntityNotFoundException("Macro", macro_id)

        await self._macro_repository.delete(macro_uuid)

        logger.info("Macro deleted", macro_id=macro_id)
