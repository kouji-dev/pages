"""Issue activity database model."""

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class IssueActivityModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Issue activity database model.

    Stores activity logs for issue changes (creation, updates, deletions).
    """

    __tablename__ = "issue_activities"

    issue_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )  # User who performed the action

    # Action type
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # created, updated, deleted, status_changed, assigned, etc.

    # Field change details (for updates)
    field_name: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # title, status, priority, assignee_id, etc.
    old_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # Previous value (as string)
    new_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # New value (as string)

    # Relationships
    issue = relationship(
        "IssueModel",
        back_populates="activities",
    )
    user = relationship(
        "UserModel",
        back_populates="issue_activities",
    )

    def __repr__(self) -> str:
        return (
            f"<IssueActivity(id={self.id}, issue_id={self.issue_id}, "
            f"action={self.action}, field={self.field_name})>"
        )
