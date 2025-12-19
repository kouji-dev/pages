"""Get macro use case."""

from uuid import UUID

import structlog

from src.application.dtos.macro import MacroResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import MacroRepository

logger = structlog.get_logger()


class GetMacroUseCase:
    """Use case for getting a macro by ID."""

    def __init__(self, macro_repository: MacroRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            macro_repository: Macro repository
        """
        self._macro_repository = macro_repository

    async def execute(self, macro_id: str) -> MacroResponse:
        """Execute get macro.

        Args:
            macro_id: Macro ID

        Returns:
            Macro response DTO

        Raises:
            EntityNotFoundException: If macro not found
        """
        logger.info("Getting macro", macro_id=macro_id)

        macro_uuid = UUID(macro_id)
        macro = await self._macro_repository.get_by_id(macro_uuid)

        if macro is None:
            logger.warning("Macro not found", macro_id=macro_id)
            raise EntityNotFoundException("Macro", macro_id)

        logger.info("Macro retrieved", macro_id=macro_id)

        return MacroResponse(
            id=macro.id,
            name=macro.name,
            code=macro.code,
            config_schema=macro.config_schema,
            macro_type=macro.macro_type,
            is_system=macro.is_system,
            created_at=macro.created_at,
            updated_at=macro.updated_at,
        )
