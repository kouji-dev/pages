"""API v1 routes."""

from fastapi import APIRouter

from src.presentation.api.v1.auth import router as auth_router
from src.presentation.api.v1.health import router as health_router
from src.presentation.api.v1.organizations import router as organizations_router
from src.presentation.api.v1.projects import router as projects_router
from src.presentation.api.v1.users import router as users_router

router = APIRouter(prefix="/api/v1")

# Include route modules
router.include_router(health_router, tags=["Health"])
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(organizations_router, prefix="/organizations", tags=["Organizations"])
router.include_router(projects_router, prefix="/projects", tags=["Projects"])
