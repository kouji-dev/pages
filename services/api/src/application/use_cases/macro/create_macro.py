"""Create macro use case."""

import structlog

from src.application.dtos.macro import CreateMacroRequest, MacroResponse
from src.domain.entities import Macro
from src.domain.repositories import MacroRepository

logger = structlog.get_logger()


class CreateMacroUseCase:
    """Use case for creating a macro."""

    def __init__(self, macro_repository: MacroRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            macro_repository: Macro repository
        """
        self._macro_repository = macro_repository

    async def execute(self, request: CreateMacroRequest) -> MacroResponse:
        """Execute create macro.

        Args:
            request: Create macro request

        Returns:
            Created macro response DTO

        Raises:
            ValueError: If macro name already exists
        """
        logger.info("Creating macro", name=request.name, macro_type=request.macro_type)

        # Check if macro with same name exists
        existing = await self._macro_repository.get_by_name(request.name)
        if existing:
            logger.warning("Macro with name already exists", name=request.name)
            raise ValueError(f"Macro with name '{request.name}' already exists")

        # Create macro entity
        macro = Macro.create(
            name=request.name,
            code=request.code,
            macro_type=request.macro_type,
            config_schema=request.config_schema,
            is_system=request.is_system,
        )

        # Persist macro
        created_macro = await self._macro_repository.create(macro)

        logger.info("Macro created", macro_id=str(created_macro.id), name=request.name)

        return MacroResponse(
            id=created_macro.id,
            name=created_macro.name,
            code=created_macro.code,
            config_schema=created_macro.config_schema,
            macro_type=created_macro.macro_type,
            is_system=created_macro.is_system,
            created_at=created_macro.created_at,
            updated_at=created_macro.updated_at,
        )
