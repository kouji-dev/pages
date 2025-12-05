"""API v1 routes."""

from fastapi import APIRouter

from src.presentation.api.v1.auth import router as auth_router
from src.presentation.api.v1.health import router as health_router

router = APIRouter(prefix="/api/v1")

# Include route modules
router.include_router(health_router, tags=["Health"])
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

