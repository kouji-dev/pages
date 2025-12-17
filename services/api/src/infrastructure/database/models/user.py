"""User database model."""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class UserModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """User database model.

    Stores user account information including authentication data.
    """

    __tablename__ = "users"

    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Profile
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    avatar_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    language: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
        default="en",
        server_default="en",
        index=True,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Preferences (JSON)
    preferences: Mapped[str | None] = mapped_column(
        Text,  # Store as JSON string
        nullable=True,
    )

    # Relationships
    organization_memberships = relationship(
        "OrganizationMemberModel",
        back_populates="user",
        lazy="selectin",
    )
    project_memberships = relationship(
        "ProjectMemberModel",
        back_populates="user",
        lazy="selectin",
    )
    created_issues = relationship(
        "IssueModel",
        foreign_keys="IssueModel.reporter_id",
        back_populates="reporter",
        lazy="selectin",
    )
    assigned_issues = relationship(
        "IssueModel",
        foreign_keys="IssueModel.assignee_id",
        back_populates="assignee",
        lazy="selectin",
    )
    comments = relationship(
        "CommentModel",
        back_populates="user",
        lazy="selectin",
    )
    notifications = relationship(
        "NotificationModel",
        back_populates="user",
        lazy="selectin",
    )
    issue_activities = relationship(
        "IssueActivityModel",
        back_populates="user",
        lazy="selectin",
    )
    time_entries = relationship(
        "TimeEntryModel",
        back_populates="user",
        lazy="selectin",
    )
    dashboards = relationship(
        "DashboardModel",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    saved_filters = relationship(
        "SavedFilterModel",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
