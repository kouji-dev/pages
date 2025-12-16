"""API v1 routes."""

from fastapi import APIRouter

from src.presentation.api.v1.attachments import router as attachments_router
from src.presentation.api.v1.auth import router as auth_router
from src.presentation.api.v1.backlog import router as backlog_router
from src.presentation.api.v1.comments import router as comments_router
from src.presentation.api.v1.health import router as health_router
from src.presentation.api.v1.issues import router as issues_router
from src.presentation.api.v1.languages import router as languages_router
from src.presentation.api.v1.notifications import router as notifications_router
from src.presentation.api.v1.organizations import router as organizations_router
from src.presentation.api.v1.pages import router as pages_router
from src.presentation.api.v1.projects import router as projects_router
from src.presentation.api.v1.search import router as search_router
from src.presentation.api.v1.spaces import router as spaces_router
from src.presentation.api.v1.sprints import router as sprints_router
from src.presentation.api.v1.templates import router as templates_router
from src.presentation.api.v1.users import router as users_router

router = APIRouter(prefix="/api/v1")

# Include route modules
router.include_router(health_router, tags=["Health"])
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(languages_router, tags=["Languages"])
router.include_router(organizations_router, prefix="/organizations", tags=["Organizations"])
router.include_router(notifications_router, tags=["Notifications"])
router.include_router(search_router, tags=["Search"])
router.include_router(projects_router, prefix="/projects", tags=["Projects"])
router.include_router(sprints_router, tags=["Sprints"])
router.include_router(backlog_router, tags=["Backlog"])
router.include_router(issues_router, prefix="/issues", tags=["Issues"])
router.include_router(comments_router, tags=["Comments"])
router.include_router(attachments_router, tags=["Attachments"])
router.include_router(spaces_router, prefix="/spaces", tags=["Spaces"])
router.include_router(pages_router, prefix="/pages", tags=["Pages"])
router.include_router(templates_router, prefix="/templates", tags=["Templates"])
