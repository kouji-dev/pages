"""FastAPI application entry point."""

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.domain.exceptions import DomainException
from src.infrastructure.config import get_settings
from src.presentation.api import v1_router
from src.presentation.middlewares import (
    RequestIDMiddleware,
    domain_exception_handler,
    generic_exception_handler,
    limiter,
    rate_limit_handler,
    validation_exception_handler,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        (
            structlog.dev.ConsoleRenderer()
            if get_settings().debug
            else structlog.processors.JSONRenderer()
        ),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def create_app(enable_rate_limiting: bool = True) -> FastAPI:
    """Create and configure FastAPI application.

    Args:
        enable_rate_limiting: Whether to enable rate limiting middleware (default: True).
                              Set to False for testing.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Pages API - Project Management and Documentation Platform",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    # Add request ID middleware (first to track all requests)
    app.add_middleware(RequestIDMiddleware)

    # Add rate limiting middleware (disabled in tests)
    if enable_rate_limiting:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
        app.add_middleware(SlowAPIMiddleware)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Include API routers
    app.include_router(v1_router)

    @app.on_event("startup")
    async def startup_event() -> None:
        """Application startup handler."""
        from src.infrastructure.database import init_db

        logger.info(
            "Starting application",
            app_name=settings.app_name,
            version=settings.app_version,
            environment=settings.environment,
        )

        # Initialize database tables (in development)
        # In production, use Alembic migrations instead
        if settings.debug:
            try:
                await init_db()
                logger.info("Database tables initialized")
            except Exception as e:
                logger.warning(f"Database initialization skipped: {e}")

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        """Application shutdown handler."""
        from src.infrastructure.database import close_db

        logger.info("Shutting down application")
        await close_db()

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
