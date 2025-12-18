"""Execute macro use case."""

import structlog

from src.application.dtos.macro import ExecuteMacroRequest, ExecuteMacroResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import MacroRepository

logger = structlog.get_logger()


class ExecuteMacroUseCase:
    """Use case for executing a macro."""

    def __init__(self, macro_repository: MacroRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            macro_repository: Macro repository
        """
        self._macro_repository = macro_repository

    async def execute(self, request: ExecuteMacroRequest) -> ExecuteMacroResponse:
        """Execute macro.

        Args:
            request: Execute macro request

        Returns:
            Macro execution response DTO

        Raises:
            EntityNotFoundException: If macro not found
            ValueError: If macro execution fails
        """
        logger.info("Executing macro", macro_name=request.macro_name)

        macro = await self._macro_repository.get_by_name(request.macro_name)

        if macro is None:
            logger.warning("Macro not found for execution", macro_name=request.macro_name)
            raise EntityNotFoundException("Macro", request.macro_name)

        # Execute macro code with config
        try:
            output = await self._execute_macro_code(macro.code, request.config)
        except Exception as e:
            logger.error("Macro execution failed", macro_name=request.macro_name, error=str(e))
            raise ValueError(f"Macro execution failed: {str(e)}") from e

        logger.info("Macro executed", macro_name=request.macro_name)

        return ExecuteMacroResponse(
            output=output,
            macro_name=request.macro_name,
        )

    async def _execute_macro_code(self, code: str, config: dict[str, str]) -> str:
        """Execute macro code with configuration.

        Args:
            code: Macro code
            config: Macro configuration

        Returns:
            Rendered HTML output

        Note:
            This is a simplified macro execution engine.
            In production, you'd want a more sophisticated system with sandboxing.
        """
        # Simple template replacement: {{key}} -> config value
        output = code
        for key, value in config.items():
            placeholder = f"{{{{{key}}}}}"
            output = output.replace(placeholder, str(value))

        # Handle default macros
        if "info_panel" in code.lower() or "info" in code.lower():
            title = config.get("title", "Info")
            content = config.get("content", "")
            output = f'<div class="info-panel"><h3>{title}</h3><p>{content}</p></div>'
        elif "warning_panel" in code.lower() or "warning" in code.lower():
            title = config.get("title", "Warning")
            content = config.get("content", "")
            output = f'<div class="warning-panel"><h3>{title}</h3><p>{content}</p></div>'
        elif "error_panel" in code.lower() or "error" in code.lower():
            title = config.get("title", "Error")
            content = config.get("content", "")
            output = f'<div class="error-panel"><h3>{title}</h3><p>{content}</p></div>'
        elif "code_block" in code.lower():
            language = config.get("language", "")
            code_content = config.get("code", "")
            output = f'<pre><code class="language-{language}">{code_content}</code></pre>'

        return output
