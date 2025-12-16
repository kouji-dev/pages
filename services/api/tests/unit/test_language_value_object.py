"""Unit tests for Language value object."""

import pytest

from src.domain.value_objects.language import Language


class TestLanguage:
    """Tests for Language value object."""

    def test_create_valid_language(self) -> None:
        """Test creating a valid language."""
        language = Language("en")
        assert language.code == "en"
        assert language.base_code == "en"
        assert language.name == "English"

    def test_create_language_with_region(self) -> None:
        """Test creating a language with region code."""
        language = Language("en-US")
        assert language.code == "en-us"  # Normalized to lowercase
        assert language.base_code == "en"
        assert language.name == "English"

    def test_create_language_case_insensitive(self) -> None:
        """Test language code is case insensitive."""
        language1 = Language("EN")
        language2 = Language("en")
        assert language1.code == language2.code == "en"

    def test_create_language_strips_whitespace(self) -> None:
        """Test language code strips whitespace."""
        language = Language("  fr  ")
        assert language.code == "fr"

    def test_from_string_with_valid_code(self) -> None:
        """Test from_string with valid code."""
        language = Language.from_string("es")
        assert language.code == "es"
        assert language.name == "Español"

    def test_from_string_with_none(self) -> None:
        """Test from_string with None returns default language."""
        language = Language.from_string(None)
        assert language.code == Language.DEFAULT_LANGUAGE
        assert language.name == "English"

    def test_from_string_with_empty_string(self) -> None:
        """Test from_string with empty string returns default language."""
        language = Language.from_string("")
        assert language.code == Language.DEFAULT_LANGUAGE

    def test_invalid_empty_code(self) -> None:
        """Test that empty language code raises ValueError."""
        with pytest.raises(ValueError, match="Language code cannot be empty"):
            Language("")

    def test_invalid_non_string_code(self) -> None:
        """Test that non-string code raises ValueError."""
        with pytest.raises(ValueError, match="Language code must be a string"):
            Language(123)  # type: ignore

    def test_invalid_too_short_code(self) -> None:
        """Test that too short code raises ValueError."""
        with pytest.raises(ValueError, match="Language code must be 2-5 characters"):
            Language("e")

    def test_invalid_too_long_code(self) -> None:
        """Test that too long code raises ValueError."""
        with pytest.raises(ValueError, match="Language code must be 2-5 characters"):
            Language("toolong")

    def test_unsupported_language(self) -> None:
        """Test that unsupported language raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported language: zh"):
            Language("zh")

    def test_get_supported_languages(self) -> None:
        """Test getting list of supported languages."""
        supported = Language.get_supported_languages()
        assert len(supported) == 4  # en, fr, es, de
        assert any(lang["code"] == "en" and lang["name"] == "English" for lang in supported)
        assert any(lang["code"] == "fr" and lang["name"] == "Français" for lang in supported)
        assert any(lang["code"] == "es" and lang["name"] == "Español" for lang in supported)
        assert any(lang["code"] == "de" and lang["name"] == "Deutsch" for lang in supported)

    def test_string_representation(self) -> None:
        """Test string representation of language."""
        language = Language("fr")
        assert str(language) == "fr"

    def test_language_immutable(self) -> None:
        """Test that language is immutable (frozen dataclass)."""
        from dataclasses import FrozenInstanceError

        language = Language("en")
        with pytest.raises(FrozenInstanceError):
            language.code = "fr"  # type: ignore
