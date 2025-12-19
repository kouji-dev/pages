"""Domain repository interfaces (ports)."""

from src.domain.repositories.attachment_repository import AttachmentRepository
from src.domain.repositories.comment_repository import CommentRepository
from src.domain.repositories.custom_field_repository import (
    CustomFieldRepository,
    CustomFieldValueRepository,
)
from src.domain.repositories.dashboard_repository import DashboardRepository
from src.domain.repositories.favorite_repository import FavoriteRepository
from src.domain.repositories.folder_repository import FolderRepository
from src.domain.repositories.invitation_repository import InvitationRepository
from src.domain.repositories.issue_activity_repository import IssueActivityRepository
from src.domain.repositories.issue_link_repository import IssueLinkRepository
from src.domain.repositories.issue_repository import IssueRepository
from src.domain.repositories.macro_repository import MacroRepository
from src.domain.repositories.notification_repository import NotificationRepository
from src.domain.repositories.organization_repository import OrganizationRepository
from src.domain.repositories.page_permission_repository import (
    PagePermissionRepository,
    SpacePermissionRepository,
)
from src.domain.repositories.page_repository import PageRepository
from src.domain.repositories.page_version_repository import PageVersionRepository
from src.domain.repositories.presence_repository import PresenceRepository
from src.domain.repositories.project_repository import ProjectRepository
from src.domain.repositories.saved_filter_repository import SavedFilterRepository
from src.domain.repositories.space_repository import SpaceRepository
from src.domain.repositories.sprint_repository import SprintRepository
from src.domain.repositories.template_repository import TemplateRepository
from src.domain.repositories.time_entry_repository import TimeEntryRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.whiteboard_repository import WhiteboardRepository
from src.domain.repositories.workflow_repository import WorkflowRepository

__all__ = [
    "UserRepository",
    "OrganizationRepository",
    "InvitationRepository",
    "ProjectRepository",
    "IssueRepository",
    "IssueActivityRepository",
    "CommentRepository",
    "AttachmentRepository",
    "SpaceRepository",
    "PageRepository",
    "PageVersionRepository",
    "PagePermissionRepository",
    "SpacePermissionRepository",
    "MacroRepository",
    "PresenceRepository",
    "WhiteboardRepository",
    "TemplateRepository",
    "NotificationRepository",
    "SprintRepository",
    "WorkflowRepository",
    "CustomFieldRepository",
    "CustomFieldValueRepository",
    "IssueLinkRepository",
    "TimeEntryRepository",
    "DashboardRepository",
    "SavedFilterRepository",
    "FolderRepository",
    "FavoriteRepository",
]
