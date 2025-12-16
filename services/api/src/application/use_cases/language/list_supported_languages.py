"""List supported languages use case."""

import structlog

from src.application.dtos.language import LanguageInfo, SupportedLanguagesResponse
from src.domain.value_objects.language import Language

logger = structlog.get_logger()


class ListSupportedLanguagesUseCase:
    """Use case for listing supported languages."""

    async def execute(self) -> SupportedLanguagesResponse:
        """Execute list supported languages.

        Returns:
            SupportedLanguagesResponse with list of supported languages
        """
        logger.info("Listing supported languages")

        # Get supported languages from Language value object
        supported_languages = Language.get_supported_languages()

        # Convert to DTO
        language_infos = [
            LanguageInfo(code=lang["code"], name=lang["name"]) for lang in supported_languages
        ]

        logger.info("Supported languages retrieved", count=len(language_infos))

        return SupportedLanguagesResponse(languages=language_infos)
