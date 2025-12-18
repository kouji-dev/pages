"""SQLAlchemy database models."""

from src.infrastructure.database.models.attachment import AttachmentModel
from src.infrastructure.database.models.comment import CommentModel
from src.infrastructure.database.models.custom_field import (
    CustomFieldModel,
    CustomFieldValueModel,
)
from src.infrastructure.database.models.dashboard import (
    DashboardModel,
    DashboardWidgetModel,
)
from src.infrastructure.database.models.favorite import FavoriteModel
from src.infrastructure.database.models.folder import FolderModel
from src.infrastructure.database.models.invitation import InvitationModel
from src.infrastructure.database.models.issue import IssueModel
from src.infrastructure.database.models.issue_activity import IssueActivityModel
from src.infrastructure.database.models.issue_link import IssueLinkModel
from src.infrastructure.database.models.macro import MacroModel
from src.infrastructure.database.models.notification import NotificationModel
from src.infrastructure.database.models.organization import (
    OrganizationMemberModel,
    OrganizationModel,
)
from src.infrastructure.database.models.page import PageModel, SpaceModel
from src.infrastructure.database.models.page_permission import (
    PagePermissionModel,
    SpacePermissionModel,
)
from src.infrastructure.database.models.page_version import PageVersionModel
from src.infrastructure.database.models.presence import PresenceModel
from src.infrastructure.database.models.project import (
    ProjectMemberModel,
    ProjectModel,
)
from src.infrastructure.database.models.saved_filter import SavedFilterModel
from src.infrastructure.database.models.sprint import SprintIssueModel, SprintModel
from src.infrastructure.database.models.template import TemplateModel
from src.infrastructure.database.models.time_entry import TimeEntryModel
from src.infrastructure.database.models.user import UserModel
from src.infrastructure.database.models.whiteboard import WhiteboardModel
from src.infrastructure.database.models.workflow import (
    WorkflowModel,
    WorkflowStatusModel,
    WorkflowTransitionModel,
)

__all__ = [
    "UserModel",
    "OrganizationModel",
    "OrganizationMemberModel",
    "InvitationModel",
    "ProjectModel",
    "ProjectMemberModel",
    "IssueModel",
    "IssueActivityModel",
    "CommentModel",
    "PageModel",
    "SpaceModel",
    "PageVersionModel",
    "PagePermissionModel",
    "SpacePermissionModel",
    "PresenceModel",
    "MacroModel",
    "TemplateModel",
    "WhiteboardModel",
    "AttachmentModel",
    "NotificationModel",
    "SprintModel",
    "SprintIssueModel",
    "WorkflowModel",
    "WorkflowStatusModel",
    "WorkflowTransitionModel",
    "CustomFieldModel",
    "CustomFieldValueModel",
    "IssueLinkModel",
    "TimeEntryModel",
    "DashboardModel",
    "DashboardWidgetModel",
    "SavedFilterModel",
    "FolderModel",
    "FavoriteModel",
]
