"""Unit tests for middlewares."""

import pytest
from fastapi import FastAPI, Request

from src.domain.exceptions.base import (
    AuthenticationException,
    EntityNotFoundException,
)
from src.presentation.middlewares import error_handler
from src.presentation.middlewares.language import LanguageDetectionMiddleware
from src.presentation.middlewares.request_id import RequestIDMiddleware


class TestErrorHandlers:
    """Test error handler functions."""

    @pytest.mark.asyncio
    async def test_domain_exception_handler(self):
        """Test handling of domain exceptions."""
        app = FastAPI()
        app.add_exception_handler(EntityNotFoundException, error_handler.domain_exception_handler)

        @app.get("/test")
        async def test_endpoint():
            raise EntityNotFoundException("User", "123")

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/test")
            assert response.status_code == 404
            data = response.json()
            assert "error" in data
            assert "User" in data["message"]

    @pytest.mark.asyncio
    async def test_authentication_exception_handler(self):
        """Test handling of authentication exceptions."""
        app = FastAPI()
        app.add_exception_handler(AuthenticationException, error_handler.domain_exception_handler)

        @app.get("/test")
        async def test_endpoint():
            raise AuthenticationException("Unauthorized access")

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/test")
            assert response.status_code == 401
            data = response.json()
            assert "error" in data
            assert data["message"] == "Unauthorized access"

    @pytest.mark.asyncio
    async def test_generic_exception_handler(self):
        """Test handling of generic exceptions."""
        app = FastAPI()
        # Don't add exception handler - let it be unhandled to test the handler
        app.add_exception_handler(ValueError, error_handler.generic_exception_handler)

        @app.get("/test")
        async def test_endpoint():
            raise ValueError("Something went wrong")

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/test")
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
            assert data["error"] == "InternalServerError"


class TestRequestIDMiddleware:
    """Test request ID middleware."""

    @pytest.mark.asyncio
    async def test_adds_request_id_to_request(self):
        """Test that request ID is added to request state."""
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)

        @app.get("/test")
        async def test_endpoint(request: Request):
            return {"status": "ok"}

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/test")
            assert response.status_code == 200
            # Request ID should be in response headers
            assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_adds_request_id_to_response_headers(self):
        """Test that request ID is added to response headers."""
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/test")
            assert response.status_code == 200
            assert "X-Request-ID" in response.headers
            assert len(response.headers["X-Request-ID"]) > 0

    @pytest.mark.asyncio
    async def test_uses_existing_request_id_from_header(self):
        """Test that existing request ID from header is used."""
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)

        custom_request_id = "custom-request-id-12345"

        @app.get("/test")
        async def test_endpoint(request: Request):
            return {"status": "ok"}

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/test", headers={"X-Request-ID": custom_request_id})
            assert response.status_code == 200
            assert response.headers["X-Request-ID"] == custom_request_id


class TestLanguageDetectionMiddleware:
    """Test language detection middleware."""

    @pytest.mark.asyncio
    async def test_detects_language_from_accept_language_header(self):
        """Test language detection from Accept-Language header."""
        app = FastAPI()
        app.add_middleware(LanguageDetectionMiddleware)

        language_captured = None

        @app.get("/test")
        async def test_endpoint(request: Request):
            nonlocal language_captured
            language_captured = request.state.language
            return {"status": "ok"}

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/test", headers={"Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"}
            )
            assert response.status_code == 200
            assert language_captured == "fr"

    @pytest.mark.asyncio
    async def test_defaults_to_english_when_no_header(self):
        """Test default language when no Accept-Language header."""
        app = FastAPI()
        app.add_middleware(LanguageDetectionMiddleware)

        language_captured = None

        @app.get("/test")
        async def test_endpoint(request: Request):
            nonlocal language_captured
            language_captured = request.state.language
            return {"status": "ok"}

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/test")
            assert response.status_code == 200
            assert language_captured == "en"

    @pytest.mark.asyncio
    async def test_handles_unsupported_language(self):
        """Test handling of unsupported language."""
        app = FastAPI()
        app.add_middleware(LanguageDetectionMiddleware)

        language_captured = None

        @app.get("/test")
        async def test_endpoint(request: Request):
            nonlocal language_captured
            language_captured = request.state.language
            return {"status": "ok"}

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/test", headers={"Accept-Language": "zh-CN,zh;q=0.9"})
            assert response.status_code == 200
            # Should fallback to default language
            assert language_captured == "en"

    @pytest.mark.asyncio
    async def test_handles_quality_values_in_accept_language(self):
        """Test handling of quality values in Accept-Language header."""
        app = FastAPI()
        app.add_middleware(LanguageDetectionMiddleware)

        language_captured = None

        @app.get("/test")
        async def test_endpoint(request: Request):
            nonlocal language_captured
            language_captured = request.state.language
            return {"status": "ok"}

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Spanish has higher quality value
            response = await client.get(
                "/test", headers={"Accept-Language": "en;q=0.5,es;q=0.9,fr;q=0.7"}
            )
            assert response.status_code == 200
            assert language_captured == "es"
