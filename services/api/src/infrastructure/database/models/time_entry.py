"""Time entry database model."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class TimeEntryModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Time entry database model."""

    __tablename__ = "time_entries"

    issue_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    hours: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    issue = relationship(
        "IssueModel",
        back_populates="time_entries",
    )
    user = relationship(
        "UserModel",
        back_populates="time_entries",
    )

    def __repr__(self) -> str:
        return (
            f"<TimeEntry(id={self.id}, issue_id={self.issue_id}, "
            f"user_id={self.user_id}, hours={self.hours})>"
        )
