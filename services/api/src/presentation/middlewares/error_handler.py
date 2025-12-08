"""Error handling middleware and exception handlers."""

from typing import Any

import structlog
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.domain.exceptions import (
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    DomainException,
    EntityNotFoundException,
    ValidationException,
)

logger = structlog.get_logger()


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Handle domain exceptions and return appropriate HTTP responses."""

    # Map domain exceptions to HTTP status codes
    status_code_map = {
        EntityNotFoundException: status.HTTP_404_NOT_FOUND,
        ValidationException: status.HTTP_400_BAD_REQUEST,
        AuthenticationException: status.HTTP_401_UNAUTHORIZED,
        AuthorizationException: status.HTTP_403_FORBIDDEN,
        ConflictException: status.HTTP_409_CONFLICT,
    }

    status_code = status_code_map.get(type(exc), status.HTTP_400_BAD_REQUEST)

    logger.warning(
        "Domain exception",
        exception_type=type(exc).__name__,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )

    response_content: dict[str, Any] = {
        "error": type(exc).__name__,
        "message": exc.message,
    }

    if exc.details:
        response_content["details"] = exc.details

    return JSONResponse(
        status_code=status_code,
        content=response_content,
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""

    logger.warning(
        "Validation error",
        errors=exc.errors(),
        path=request.url.path,
    )

    # Format validation errors
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(
            {
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": errors,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""

    logger.exception(
        "Unexpected error",
        exception_type=type(exc).__name__,
        message=str(exc),
        path=request.url.path,
    )

    # Get settings to check if debug mode is enabled
    from src.infrastructure.config import get_settings

    settings = get_settings()
    error_details: dict[str, str | dict[str, str] | list[str]] = {
        "error": "InternalServerError",
        "message": "An unexpected error occurred",
    }

    # Include error details in debug mode
    if settings.debug:
        error_details["details"] = {
            "exception_type": type(exc).__name__,
            "message": str(exc),
        }
        import traceback

        error_details["traceback"] = traceback.format_exc().split("\n")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_details,
    )
