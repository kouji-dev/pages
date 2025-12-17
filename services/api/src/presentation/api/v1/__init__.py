"""API v1 routes."""

from fastapi import APIRouter

from src.presentation.api.v1.attachments import router as attachments_router
from src.presentation.api.v1.auth import router as auth_router
from src.presentation.api.v1.backlog import router as backlog_router
from src.presentation.api.v1.comments import router as comments_router
from src.presentation.api.v1.custom_fields import router as custom_fields_router
from src.presentation.api.v1.dashboards import router as dashboards_router
from src.presentation.api.v1.favorites import router as favorites_router
from src.presentation.api.v1.folders import router as folders_router
from src.presentation.api.v1.health import router as health_router
from src.presentation.api.v1.issue_links import router as issue_links_router
from src.presentation.api.v1.issues import router as issues_router
from src.presentation.api.v1.languages import router as languages_router
from src.presentation.api.v1.nodes import router as nodes_router
from src.presentation.api.v1.notifications import router as notifications_router
from src.presentation.api.v1.organizations import router as organizations_router
from src.presentation.api.v1.pages import router as pages_router
from src.presentation.api.v1.projects import router as projects_router
from src.presentation.api.v1.saved_filters import router as saved_filters_router
from src.presentation.api.v1.search import router as search_router
from src.presentation.api.v1.spaces import router as spaces_router
from src.presentation.api.v1.sprints import router as sprints_router
from src.presentation.api.v1.subtasks import router as subtasks_router
from src.presentation.api.v1.templates import router as templates_router
from src.presentation.api.v1.time_entries import router as time_entries_router
from src.presentation.api.v1.users import router as users_router
from src.presentation.api.v1.workflows import router as workflows_router

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
router.include_router(folders_router, tags=["Folders"])
router.include_router(nodes_router, tags=["Nodes"])
router.include_router(favorites_router, tags=["Favorites"])
router.include_router(attachments_router, tags=["Attachments"])
router.include_router(spaces_router, prefix="/spaces", tags=["Spaces"])
router.include_router(pages_router, prefix="/pages", tags=["Pages"])
router.include_router(templates_router, prefix="/templates", tags=["Templates"])
router.include_router(workflows_router, tags=["Workflows"])
router.include_router(custom_fields_router, tags=["Custom Fields"])
router.include_router(time_entries_router, tags=["Time Entries"])
router.include_router(issue_links_router, tags=["Issue Links"])
router.include_router(dashboards_router, tags=["Dashboards"])
router.include_router(subtasks_router, tags=["Subtasks"])
router.include_router(saved_filters_router, tags=["Saved Filters"])
router.include_router(folders_router, tags=["Folders"])
router.include_router(nodes_router, tags=["Nodes"])
router.include_router(favorites_router, tags=["Favorites"])
