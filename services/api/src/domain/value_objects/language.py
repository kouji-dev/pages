"""Language value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Language:
    """Language value object.

    Represents a language code following ISO 639-1 standard.
    """

    code: str

    # Supported languages (ISO 639-1 codes)
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "fr": "Français",
        "es": "Español",
        "de": "Deutsch",
    }

    DEFAULT_LANGUAGE = "en"

    def __post_init__(self) -> None:
        """Validate language code."""
        if not self.code:
            raise ValueError("Language code cannot be empty")

        if not isinstance(self.code, str):
            raise ValueError("Language code must be a string")

        # Normalize to lowercase
        object.__setattr__(self, "code", self.code.lower().strip())

        if len(self.code) < 2 or len(self.code) > 5:
            raise ValueError("Language code must be 2-5 characters (e.g., 'en', 'en-US')")

        # Extract base language code (e.g., 'en' from 'en-US')
        base_code = self.code.split("-")[0]

        if base_code not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {self.code}. "
                f"Supported languages: {', '.join(self.SUPPORTED_LANGUAGES.keys())}"
            )

    @property
    def base_code(self) -> str:
        """Get base language code (without region).

        Returns:
            Base language code (e.g., 'en' from 'en-US')
        """
        return self.code.split("-")[0]

    @property
    def name(self) -> str:
        """Get language name.

        Returns:
            Human-readable language name
        """
        return self.SUPPORTED_LANGUAGES.get(self.base_code, self.code)

    @classmethod
    def from_string(cls, code: str | None) -> "Language":
        """Create Language from string code.

        Args:
            code: Language code string (e.g., 'en', 'fr', 'en-US')

        Returns:
            Language value object

        Raises:
            ValueError: If code is invalid
        """
        if not code:
            return cls(cls.DEFAULT_LANGUAGE)

        return cls(code)

    @classmethod
    def get_supported_languages(cls) -> list[dict[str, str]]:
        """Get list of supported languages.

        Returns:
            List of dictionaries with 'code' and 'name' keys
        """
        return [{"code": code, "name": name} for code, name in cls.SUPPORTED_LANGUAGES.items()]

    def __str__(self) -> str:
        """String representation."""
        return self.code
