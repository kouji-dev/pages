"""Label and IssueLabel database models."""

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class LabelModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Label database model.

    Labels belong to a project and can be attached to issues.
    """

    __tablename__ = "labels"
    __table_args__ = (UniqueConstraint("project_id", "name", name="uq_label_project_name"),)

    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    color: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
    )  # Hex color e.g. #3b82f6
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    project = relationship(
        "ProjectModel",
        back_populates="labels",
    )
    issue_labels = relationship(
        "IssueLabelModel",
        back_populates="label",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Label(id={self.id}, name={self.name}, project_id={self.project_id})>"


class IssueLabelModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Issue-Label association model (many-to-many)."""

    __tablename__ = "issue_labels"
    __table_args__ = (UniqueConstraint("issue_id", "label_id", name="uq_issue_label"),)

    issue_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("labels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    issue = relationship(
        "IssueModel",
        back_populates="issue_labels",
    )
    label = relationship(
        "LabelModel",
        back_populates="issue_labels",
    )

    def __repr__(self) -> str:
        return f"<IssueLabel(issue_id={self.issue_id}, label_id={self.label_id})>"
