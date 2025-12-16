"""Unit tests for language detection middleware."""

from unittest.mock import MagicMock

import pytest
from fastapi import Request
from starlette.responses import Response

from src.presentation.middlewares.language import LanguageDetectionMiddleware


@pytest.fixture
def mock_call_next():
    """Create a mock call_next function."""

    async def call_next(request: Request) -> Response:
        return Response(content="OK", status_code=200)

    return call_next


@pytest.fixture
def middleware():
    """Create language detection middleware instance."""
    return LanguageDetectionMiddleware(lambda request, call_next: call_next(request))


class TestLanguageDetectionMiddleware:
    """Tests for LanguageDetectionMiddleware."""

    @pytest.mark.asyncio
    async def test_detect_language_from_accept_language_header(
        self, middleware, mock_call_next
    ) -> None:
        """Test language detection from Accept-Language header."""
        request = MagicMock(spec=Request)
        request.headers = {"Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"}
        request.url.path = "/api/v1/test"
        request.state = MagicMock()

        response = await middleware.dispatch(request, mock_call_next)

        assert response.status_code == 200
        assert request.state.language == "fr"

    @pytest.mark.asyncio
    async def test_detect_language_with_region_code(self, middleware, mock_call_next) -> None:
        """Test language detection with region code."""
        request = MagicMock(spec=Request)
        request.headers = {"Accept-Language": "en-US,en;q=0.9"}
        request.url.path = "/api/v1/test"
        request.state = MagicMock()

        response = await middleware.dispatch(request, mock_call_next)

        assert response.status_code == 200
        assert request.state.language == "en"

    @pytest.mark.asyncio
    async def test_detect_language_default_when_no_header(self, middleware, mock_call_next) -> None:
        """Test default language when no Accept-Language header."""
        request = MagicMock(spec=Request)
        request.headers = {}
        request.url.path = "/api/v1/test"
        request.state = MagicMock()

        response = await middleware.dispatch(request, mock_call_next)

        assert response.status_code == 200
        assert request.state.language == "en"  # Default

    @pytest.mark.asyncio
    async def test_detect_language_unsupported_fallback_to_default(
        self, middleware, mock_call_next
    ) -> None:
        """Test fallback to default when unsupported language in header."""
        request = MagicMock(spec=Request)
        request.headers = {"Accept-Language": "zh-CN,zh;q=0.9"}  # Chinese not supported
        request.url.path = "/api/v1/test"
        request.state = MagicMock()

        response = await middleware.dispatch(request, mock_call_next)

        assert response.status_code == 200
        assert request.state.language == "en"  # Fallback to default

    @pytest.mark.asyncio
    async def test_detect_language_quality_values(self, middleware, mock_call_next) -> None:
        """Test language detection with quality values (q-values)."""
        request = MagicMock(spec=Request)
        # Spanish has higher quality (0.9) than French (0.8)
        request.headers = {"Accept-Language": "fr;q=0.8,es;q=0.9,en;q=0.7"}
        request.url.path = "/api/v1/test"
        request.state = MagicMock()

        response = await middleware.dispatch(request, mock_call_next)

        assert response.status_code == 200
        assert request.state.language == "es"  # Highest quality supported language

    @pytest.mark.asyncio
    async def test_detect_language_multiple_supported_languages(
        self, middleware, mock_call_next
    ) -> None:
        """Test language detection with multiple supported languages."""
        request = MagicMock(spec=Request)
        request.headers = {"Accept-Language": "de,fr,es,en"}
        request.url.path = "/api/v1/test"
        request.state = MagicMock()

        response = await middleware.dispatch(request, mock_call_next)

        assert response.status_code == 200
        assert request.state.language == "de"  # First supported language

    @pytest.mark.asyncio
    async def test_parse_accept_language_simple(self, middleware) -> None:
        """Test parsing simple Accept-Language header."""
        languages = middleware._parse_accept_language("en")
        assert languages == ["en"]

    @pytest.mark.asyncio
    async def test_parse_accept_language_with_quality(self, middleware) -> None:
        """Test parsing Accept-Language header with quality values."""
        languages = middleware._parse_accept_language("en;q=0.9,fr;q=0.8")
        # Should be sorted by quality (descending)
        assert "en" in languages
        assert "fr" in languages
        assert languages[0] == "en"  # Higher quality first

    @pytest.mark.asyncio
    async def test_parse_accept_language_multiple(self, middleware) -> None:
        """Test parsing Accept-Language header with multiple languages."""
        languages = middleware._parse_accept_language("en-US,fr-CA,es-MX")
        assert len(languages) == 3
        assert "en-US" in languages
        assert "fr-CA" in languages
        assert "es-MX" in languages

    @pytest.mark.asyncio
    async def test_parse_accept_language_complex(self, middleware) -> None:
        """Test parsing complex Accept-Language header."""
        header = "en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7,es;q=0.6"
        languages = middleware._parse_accept_language(header)
        # Should extract all language codes
        assert "en-US" in languages
        assert "en" in languages
        assert "fr-FR" in languages
        assert "fr" in languages
        assert "es" in languages

    @pytest.mark.asyncio
    async def test_parse_accept_language_invalid_quality(self, middleware) -> None:
        """Test parsing Accept-Language with invalid quality value."""
        languages = middleware._parse_accept_language("en;q=invalid,fr")
        # Should handle invalid quality gracefully
        assert "en" in languages
        assert "fr" in languages

    @pytest.mark.asyncio
    async def test_parse_accept_language_empty(self, middleware) -> None:
        """Test parsing empty Accept-Language header."""
        languages = middleware._parse_accept_language("")
        assert languages == []

    @pytest.mark.asyncio
    async def test_parse_accept_language_whitespace(self, middleware) -> None:
        """Test parsing Accept-Language header with whitespace."""
        languages = middleware._parse_accept_language("  en  ,  fr  ")
        # Should handle whitespace
        assert "en" in languages or "  en  " in languages
        assert "fr" in languages or "  fr  " in languages

    @pytest.mark.asyncio
    async def test_parse_accept_language_empty_component(self, middleware) -> None:
        """Test parsing Accept-Language header with empty component."""
        # Test case where component[0].strip() is empty
        languages = middleware._parse_accept_language("  ,en,  ,fr")
        # Should skip empty components
        assert "en" in languages
        assert "fr" in languages
        # Should not include empty strings
        assert "" not in languages or languages.count("") == 0
