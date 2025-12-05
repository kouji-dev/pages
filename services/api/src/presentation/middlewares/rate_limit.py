"""Rate limiting middleware using slowapi."""

from fastapi import Request, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.infrastructure.config import get_settings

settings = get_settings()

# Create limiter instance
# For production, use Redis: limiter = Limiter(key_func=get_remote_address, storage_uri=settings.redis_url)
# For development, use in-memory storage
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Default rate limit
    storage_uri=str(settings.redis_url),  # Use Redis if available, falls back to memory
)


def get_rate_limiter() -> Limiter:
    """Get rate limiter instance."""
    return limiter


# Custom rate limit exceeded handler
def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Handle rate limit exceeded exception."""
    # RateLimitExceeded doesn't have retry_after attribute, use default
    retry_after = getattr(exc, "retry_after", 60)
    response = Response(
        content=f"Rate limit exceeded: {exc.detail}",
        status_code=429,
        headers={"Retry-After": str(retry_after)},
    )
    return response
