"""Project database models."""

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class ProjectModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Project database model.

    Projects belong to organizations and contain issues.
    """

    __tablename__ = "projects"
    __table_args__ = (UniqueConstraint("organization_id", "key", name="uq_project_key"),)

    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    folder_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("folders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    key: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )  # e.g., "PROJ", "DEV" - used for issue keys like PROJ-123
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    settings: Mapped[str | None] = mapped_column(
        Text,  # Store as JSON string
        nullable=True,
    )

    # Relationships
    organization = relationship(
        "OrganizationModel",
        back_populates="projects",
    )
    folder = relationship(
        "FolderModel",
        foreign_keys=[folder_id],
    )
    members = relationship(
        "ProjectMemberModel",
        back_populates="project",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    issues = relationship(
        "IssueModel",
        back_populates="project",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    sprints = relationship(
        "SprintModel",
        back_populates="project",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    workflows = relationship(
        "WorkflowModel",
        back_populates="project",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    custom_fields = relationship(
        "CustomFieldModel",
        back_populates="project",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    dashboards = relationship(
        "DashboardModel",
        back_populates="project",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    saved_filters = relationship(
        "SavedFilterModel",
        back_populates="project",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, key={self.key}, name={self.name})>"


class ProjectMemberModel(Base, TimestampMixin):
    """Project member association model.

    Links users to projects with roles.
    """

    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_member"),)

    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="member",
    )  # admin, member, viewer

    # Relationships
    project = relationship(
        "ProjectModel",
        back_populates="members",
    )
    user = relationship(
        "UserModel",
        back_populates="project_memberships",
    )

    def __repr__(self) -> str:
        return f"<ProjectMember(project={self.project_id}, user={self.user_id}, role={self.role})>"
