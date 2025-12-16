"""Translation service for i18n support."""

import json
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


class TranslationService:
    """Service for managing translations.

    Handles loading and retrieving translations for different languages.
    Uses JSON files for translation storage.
    """

    def __init__(self, translations_dir: str | Path | None = None) -> None:
        """Initialize translation service.

        Args:
            translations_dir: Directory containing translation files
                             Defaults to 'src/infrastructure/i18n/translations'
        """
        if translations_dir is None:
            # Default to translations directory relative to this file
            self._translations_dir = Path(__file__).parent / "translations"
        else:
            self._translations_dir = Path(translations_dir)

        self._translations: dict[str, dict[str, Any]] = {}
        self._default_language = "en"

        # Load translations on initialization
        self._load_translations()

    def _load_translations(self) -> None:
        """Load all translation files from the translations directory."""
        if not self._translations_dir.exists():
            logger.warning(
                "Translations directory does not exist",
                path=str(self._translations_dir),
            )
            return

        for translation_file in self._translations_dir.glob("*.json"):
            language_code = translation_file.stem
            try:
                with translation_file.open("r", encoding="utf-8") as f:
                    self._translations[language_code] = json.load(f)
                logger.info(
                    "Loaded translations",
                    language=language_code,
                    file=str(translation_file),
                )
            except (json.JSONDecodeError, OSError) as e:
                logger.error(
                    "Failed to load translation file",
                    language=language_code,
                    file=str(translation_file),
                    error=str(e),
                )

    def get_translation(
        self,
        key: str,
        language: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Get translation for a given key.

        Args:
            key: Translation key (e.g., 'auth.login.success')
            language: Language code (e.g., 'en', 'fr')
                     Falls back to default language if not provided
            **kwargs: Variables to substitute in the translation string

        Returns:
            Translated string with variables substituted
            Returns the key itself if translation not found
        """
        if language is None:
            language = self._default_language

        # Get base language code (e.g., 'en' from 'en-US')
        base_language = language.split("-")[0]

        # Try to get translation for specified language
        translations = self._translations.get(base_language)

        # Fall back to default language if not found
        if translations is None:
            translations = self._translations.get(self._default_language, {})
            if translations:
                logger.debug(
                    "Language not found, falling back to default",
                    requested_language=language,
                    default_language=self._default_language,
                )

        # Navigate through nested keys (e.g., 'auth.login.success')
        keys = key.split(".")
        value: Any = translations
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                value = None
                break

        # If translation not found, return the key itself
        if value is None or not isinstance(value, str):
            logger.debug(
                "Translation not found",
                key=key,
                language=language,
            )
            return str(key)

        # Substitute variables
        if kwargs:
            try:
                result: str = value.format(**kwargs)
                return result
            except KeyError as e:
                logger.warning(
                    "Missing variable in translation",
                    key=key,
                    language=language,
                    missing_var=str(e),
                )
                return str(value)

        return str(value)

    def get_all_translations(self, language: str) -> dict[str, Any]:
        """Get all translations for a language.

        Args:
            language: Language code (e.g., 'en', 'fr')

        Returns:
            Dictionary of all translations for the language
            Empty dict if language not found
        """
        base_language = language.split("-")[0]
        return self._translations.get(base_language, {})

    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes.

        Returns:
            List of language codes (e.g., ['en', 'fr', 'es'])
        """
        return list(self._translations.keys())

    def reload_translations(self) -> None:
        """Reload all translation files.

        Useful for development or when translations are updated at runtime.
        """
        self._translations.clear()
        self._load_translations()
