"""Unit tests for TranslationService."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from src.infrastructure.i18n.translation_service import TranslationService


class TestTranslationService:
    """Tests for TranslationService."""

    @pytest.fixture
    def temp_translations_dir(self) -> Path:
        """Create temporary translations directory with test files."""
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create English translations
            en_translations = {
                "auth": {"login": {"success": "Login successful"}},
                "user": {"not_found": "User not found"},
                "welcome": "Welcome, {name}!",
            }
            with open(temp_path / "en.json", "w", encoding="utf-8") as f:
                json.dump(en_translations, f)

            # Create French translations
            fr_translations = {
                "auth": {"login": {"success": "Connexion réussie"}},
                "user": {"not_found": "Utilisateur non trouvé"},
                "welcome": "Bienvenue, {name}!",
            }
            with open(temp_path / "fr.json", "w", encoding="utf-8") as f:
                json.dump(fr_translations, f)

            yield temp_path

    def test_load_translations(self, temp_translations_dir: Path) -> None:
        """Test loading translations from directory."""
        service = TranslationService(temp_translations_dir)

        assert "en" in service._translations
        assert "fr" in service._translations

    def test_get_translation_simple_key(self, temp_translations_dir: Path) -> None:
        """Test getting translation with simple key."""
        service = TranslationService(temp_translations_dir)

        result = service.get_translation("user.not_found", language="en")
        assert result == "User not found"

        result_fr = service.get_translation("user.not_found", language="fr")
        assert result_fr == "Utilisateur non trouvé"

    def test_get_translation_nested_key(self, temp_translations_dir: Path) -> None:
        """Test getting translation with nested key."""
        service = TranslationService(temp_translations_dir)

        result = service.get_translation("auth.login.success", language="en")
        assert result == "Login successful"

        result_fr = service.get_translation("auth.login.success", language="fr")
        assert result_fr == "Connexion réussie"

    def test_get_translation_with_variables(self, temp_translations_dir: Path) -> None:
        """Test getting translation with variable substitution."""
        service = TranslationService(temp_translations_dir)

        result = service.get_translation("welcome", language="en", name="John")
        assert result == "Welcome, John!"

        result_fr = service.get_translation("welcome", language="fr", name="Jean")
        assert result_fr == "Bienvenue, Jean!"

    def test_get_translation_key_not_found(self, temp_translations_dir: Path) -> None:
        """Test getting translation for non-existent key returns key itself."""
        service = TranslationService(temp_translations_dir)

        result = service.get_translation("nonexistent.key", language="en")
        assert result == "nonexistent.key"

    def test_get_translation_language_not_found_fallback(
        self, temp_translations_dir: Path
    ) -> None:
        """Test fallback to default language when requested language not found."""
        service = TranslationService(temp_translations_dir)

        # Request translation in unsupported language (should fallback to 'en')
        result = service.get_translation("user.not_found", language="es")
        assert result == "User not found"  # English fallback

    def test_get_translation_no_language_uses_default(
        self, temp_translations_dir: Path
    ) -> None:
        """Test using default language when no language specified."""
        service = TranslationService(temp_translations_dir)

        result = service.get_translation("user.not_found")
        assert result == "User not found"  # Default is 'en'

    def test_get_translation_with_region_code(
        self, temp_translations_dir: Path
    ) -> None:
        """Test getting translation with region code (e.g., 'en-US')."""
        service = TranslationService(temp_translations_dir)

        # Should use base language 'en' from 'en-US'
        result = service.get_translation("user.not_found", language="en-US")
        assert result == "User not found"

    def test_get_all_translations(self, temp_translations_dir: Path) -> None:
        """Test getting all translations for a language."""
        service = TranslationService(temp_translations_dir)

        translations = service.get_all_translations("en")
        assert "auth" in translations
        assert "user" in translations
        assert translations["user"]["not_found"] == "User not found"

    def test_get_all_translations_language_not_found(
        self, temp_translations_dir: Path
    ) -> None:
        """Test getting all translations for non-existent language returns empty dict."""
        service = TranslationService(temp_translations_dir)

        translations = service.get_all_translations("es")
        assert translations == {}

    def test_get_supported_languages(self, temp_translations_dir: Path) -> None:
        """Test getting list of supported languages."""
        service = TranslationService(temp_translations_dir)

        supported = service.get_supported_languages()
        assert "en" in supported
        assert "fr" in supported
        assert len(supported) == 2

    def test_reload_translations(self, temp_translations_dir: Path) -> None:
        """Test reloading translations."""
        service = TranslationService(temp_translations_dir)

        # Add new translation file
        de_translations = {"user": {"not_found": "Benutzer nicht gefunden"}}
        with open(temp_translations_dir / "de.json", "w", encoding="utf-8") as f:
            json.dump(de_translations, f)

        # Reload
        service.reload_translations()

        assert "de" in service._translations
        result = service.get_translation("user.not_found", language="de")
        assert result == "Benutzer nicht gefunden"

    def test_missing_variable_in_translation(self, temp_translations_dir: Path) -> None:
        """Test missing variable in translation returns string without substitution."""
        service = TranslationService(temp_translations_dir)

        # Try to substitute with missing variable
        result = service.get_translation("welcome", language="en")
        # Should return the original string without substitution
        assert "Welcome" in result

    def test_nonexistent_translations_directory(self) -> None:
        """Test service handles non-existent translations directory gracefully."""
        service = TranslationService("/nonexistent/path")

        # Should not raise error, just log warning
        result = service.get_translation("any.key", language="en")
        assert result == "any.key"  # Returns key when no translations loaded

