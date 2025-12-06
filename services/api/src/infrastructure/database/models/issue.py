"""Issue database model."""

from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class IssueModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Issue database model.

    Issues represent tasks, bugs, stories within a project.
    """

    __tablename__ = "issues"

    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Issue identification
    issue_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )  # Auto-incremented per project, used for key like PROJ-123

    # Content
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Type, Status, Priority
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="task",
    )  # task, bug, story, epic
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="todo",
        index=True,
    )  # todo, in_progress, done, cancelled
    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium",
    )  # low, medium, high, critical

    # Assignment
    reporter_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assignee_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Dates
    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # Estimation
    story_points: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Relationships
    project = relationship(
        "ProjectModel",
        back_populates="issues",
    )
    reporter = relationship(
        "UserModel",
        foreign_keys=[reporter_id],
        back_populates="created_issues",
    )
    assignee = relationship(
        "UserModel",
        foreign_keys=[assignee_id],
        back_populates="assigned_issues",
    )
    comments = relationship(
        "CommentModel",
        back_populates="issue",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    attachments = relationship(
        "AttachmentModel",
        primaryjoin="and_(IssueModel.id==foreign(AttachmentModel.entity_id), "
        "AttachmentModel.entity_type=='issue')",
        lazy="selectin",
        viewonly=True,
    )
    activities = relationship(
        "IssueActivityModel",
        back_populates="issue",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="IssueActivityModel.created_at.desc()",
    )

    def __repr__(self) -> str:
        return f"<Issue(id={self.id}, number={self.issue_number}, title={self.title[:30]})>"
