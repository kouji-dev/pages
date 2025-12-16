"""Sprint database models."""

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


class SprintModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Sprint database model.

    Sprints represent time-boxed iterations within a project.
    """

    __tablename__ = "sprints"

    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    goal: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        index=True,
    )
    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="planned",
        index=True,
    )  # planned, active, completed

    # Relationships
    project = relationship(
        "ProjectModel",
        back_populates="sprints",
    )
    sprint_issues = relationship(
        "SprintIssueModel",
        back_populates="sprint",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="SprintIssueModel.order",
    )

    def __repr__(self) -> str:
        return f"<Sprint(id={self.id}, name={self.name}, status={self.status})>"


class SprintIssueModel(Base, TimestampMixin):
    """Sprint-Issue junction table.

    Represents the many-to-many relationship between sprints and issues,
    with an order field for prioritization within the sprint.
    """

    __tablename__ = "sprint_issues"

    sprint_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sprints.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
        index=True,
    )
    issue_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
        index=True,
    )
    order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )  # Order within the sprint

    # Relationships
    sprint = relationship(
        "SprintModel",
        back_populates="sprint_issues",
    )
    issue = relationship(
        "IssueModel",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<SprintIssue(sprint_id={self.sprint_id}, issue_id={self.issue_id}, order={self.order})>"
