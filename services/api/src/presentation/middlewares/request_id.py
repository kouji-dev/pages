"""Request ID tracking middleware."""

import uuid
from collections.abc import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests.

    Adds a unique request ID to:
    - Response headers (X-Request-ID)
    - Logging context
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add request ID."""
        # Generate or get request ID from header
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Add request ID to logging context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
