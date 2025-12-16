"""Language detection middleware."""

from collections.abc import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.domain.value_objects.language import Language

logger = structlog.get_logger()


class LanguageDetectionMiddleware(BaseHTTPMiddleware):
    """Middleware for detecting user language preference.

    Detects language from:
    1. User's stored language preference (if authenticated)
    2. Accept-Language header
    3. Default language (English)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and detect language.

        Args:
            request: FastAPI request
            call_next: Next middleware in chain

        Returns:
            Response from next middleware
        """
        # Detect language from Accept-Language header
        language_code = self._detect_language(request)

        # Store detected language in request state for use in endpoints
        request.state.language = language_code

        logger.debug(
            "Language detected",
            language=language_code,
            path=request.url.path,
        )

        response: Response = await call_next(request)
        return response

    def _detect_language(self, request: Request) -> str:
        """Detect language from request.

        Args:
            request: FastAPI request

        Returns:
            Detected language code (e.g., 'en', 'fr')
        """
        # Try to get language from Accept-Language header
        accept_language = request.headers.get("Accept-Language")
        if accept_language:
            # Parse Accept-Language header
            # Format: "en-US,en;q=0.9,fr;q=0.8"
            languages = self._parse_accept_language(accept_language)
            if languages:
                # Get first supported language
                for lang_code in languages:
                    base_code = lang_code.split("-")[0].lower()
                    if base_code in Language.SUPPORTED_LANGUAGES:
                        return base_code

        # Default to English
        return Language.DEFAULT_LANGUAGE

    def _parse_accept_language(self, header: str) -> list[str]:
        """Parse Accept-Language header.

        Args:
            header: Accept-Language header value

        Returns:
            List of language codes sorted by quality value (descending)
        """
        languages: list[tuple[str, float]] = []
        if not header or not header.strip():
            return []

        parts = header.split(",")

        for part in parts:
            # Split language and quality value
            # Example: "en-US;q=0.9" -> ["en-US", "q=0.9"]
            components = part.strip().split(";")
            if not components or not components[0].strip():
                continue

            lang_code = components[0].strip()

            # Parse quality value (default is 1.0)
            quality = 1.0
            if len(components) > 1:
                q_part = components[1].strip()
                if q_part.startswith("q="):
                    try:
                        quality = float(q_part[2:])
                    except ValueError:
                        quality = 1.0

            languages.append((lang_code, quality))

        # Sort by quality value (descending)
        languages.sort(key=lambda x: x[1], reverse=True)

        # Return just the language codes
        return [lang[0] for lang in languages]
