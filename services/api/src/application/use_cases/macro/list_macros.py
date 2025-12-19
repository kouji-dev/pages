"""List macros use case."""

from math import ceil

import structlog

from src.application.dtos.macro import MacroListResponse, MacroResponse
from src.domain.repositories import MacroRepository

logger = structlog.get_logger()


class ListMacrosUseCase:
    """Use case for listing macros with pagination."""

    def __init__(self, macro_repository: MacroRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            macro_repository: Macro repository
        """
        self._macro_repository = macro_repository

    async def execute(
        self,
        page: int = 1,
        limit: int = 20,
        macro_type: str | None = None,
        include_system: bool = True,
    ) -> MacroListResponse:
        """Execute list macros.

        Args:
            page: Page number (1-based)
            limit: Number of macros per page
            macro_type: Optional macro type filter
            include_system: Whether to include system macros

        Returns:
            Macro list response DTO with pagination metadata
        """
        logger.info(
            "Listing macros",
            page=page,
            limit=limit,
            macro_type=macro_type,
            include_system=include_system,
        )

        offset = (page - 1) * limit

        macros = await self._macro_repository.get_all(
            skip=offset,
            limit=limit,
            macro_type=macro_type,
            include_system=include_system,
        )
        total = await self._macro_repository.count(
            macro_type=macro_type,
            include_system=include_system,
        )

        # Calculate total pages
        pages_count = ceil(total / limit) if total > 0 else 0

        macro_responses = [
            MacroResponse(
                id=macro.id,
                name=macro.name,
                code=macro.code,
                config_schema=macro.config_schema,
                macro_type=macro.macro_type,
                is_system=macro.is_system,
                created_at=macro.created_at,
                updated_at=macro.updated_at,
            )
            for macro in macros
        ]

        logger.info("Macros listed", total=total)

        return MacroListResponse(
            macros=macro_responses,
            total=total,
            page=page,
            limit=limit,
            pages_count=pages_count,
        )
