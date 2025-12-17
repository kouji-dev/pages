"""Saved filter database model."""

from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class SavedFilterModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Saved filter database model."""

    __tablename__ = "saved_filters"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    filter_criteria: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )

    # Relationships
    user = relationship(
        "UserModel",
        back_populates="saved_filters",
    )
    project = relationship(
        "ProjectModel",
        back_populates="saved_filters",
    )

    def __repr__(self) -> str:
        return f"<SavedFilter(id={self.id}, name={self.name}, user_id={self.user_id})>"
