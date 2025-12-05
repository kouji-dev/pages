"""Health check endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from src.infrastructure.config import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    version: str
    timestamp: datetime
    environment: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check API health status.
    
    Returns:
        Health status information
    """
    settings = get_settings()
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc),
        environment=settings.environment,
    )


@router.get("/health/ready")
async def readiness_check() -> dict[str, str]:
    """Check if API is ready to serve requests.
    
    This endpoint can be extended to check database connectivity, etc.
    
    Returns:
        Readiness status
    """
    # TODO: Add database connectivity check when implemented
    return {"status": "ready"}


@router.get("/health/live")
async def liveness_check() -> dict[str, str]:
    """Check if API is alive.
    
    Returns:
        Liveness status
    """
    return {"status": "alive"}

