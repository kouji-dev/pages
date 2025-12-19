"""Update macro use case."""

from uuid import UUID

import structlog

from src.application.dtos.macro import MacroResponse, UpdateMacroRequest
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import MacroRepository

logger = structlog.get_logger()


class UpdateMacroUseCase:
    """Use case for updating a macro."""

    def __init__(self, macro_repository: MacroRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            macro_repository: Macro repository
        """
        self._macro_repository = macro_repository

    async def execute(self, macro_id: str, request: UpdateMacroRequest) -> MacroResponse:
        """Execute update macro.

        Args:
            macro_id: Macro ID
            request: Update macro request

        Returns:
            Updated macro response DTO

        Raises:
            EntityNotFoundException: If macro not found
        """
        logger.info("Updating macro", macro_id=macro_id)

        macro_uuid = UUID(macro_id)
        macro = await self._macro_repository.get_by_id(macro_uuid)

        if macro is None:
            logger.warning("Macro not found for update", macro_id=macro_id)
            raise EntityNotFoundException("Macro", macro_id)

        # Update fields if provided
        if request.name is not None:
            macro.update_name(request.name)

        if request.code is not None:
            macro.update_code(request.code)

        if request.config_schema is not None:
            macro.update_config_schema(request.config_schema)

        # Persist changes
        updated_macro = await self._macro_repository.update(macro)

        logger.info("Macro updated", macro_id=macro_id)

        return MacroResponse(
            id=updated_macro.id,
            name=updated_macro.name,
            code=updated_macro.code,
            config_schema=updated_macro.config_schema,
            macro_type=updated_macro.macro_type,
            is_system=updated_macro.is_system,
            created_at=updated_macro.created_at,
            updated_at=updated_macro.updated_at,
        )
