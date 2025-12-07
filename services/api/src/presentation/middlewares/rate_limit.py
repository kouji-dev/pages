"""Rate limiting middleware using slowapi."""

from fastapi import Request, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.infrastructure.config import get_settings

settings = get_settings()

# Create limiter instance
# For production, use Redis: limiter = Limiter(key_func=get_remote_address, storage_uri=settings.redis_url)
# For development, use in-memory storage to avoid Redis connection issues
# Use in-memory storage by default in development
if settings.environment == "development" or settings.debug:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["100/minute"],
        # No storage_uri means in-memory storage
    )
else:
    # Production: use Redis
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["100/minute"],
        storage_uri=str(settings.redis_url),
    )


def get_rate_limiter() -> Limiter:
    """Get rate limiter instance."""
    return limiter


# Custom rate limit exceeded handler
def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Handle rate limit exceeded exception."""
    # RateLimitExceeded doesn't have retry_after attribute, use default
    retry_after = getattr(exc, "retry_after", 60)
    # Handle both RateLimitExceeded (has detail) and ConnectionError (doesn't have detail)
    detail = getattr(exc, "detail", str(exc))
    response = Response(
        content=f"Rate limit exceeded: {detail}",
        status_code=429,
        headers={"Retry-After": str(retry_after)},
    )
    return response
