"""Custom field database models."""

from typing import Any
from uuid import UUID

from sqlalchemy import JSON, Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class CustomFieldModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Custom field database model."""

    __tablename__ = "custom_fields"

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
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # text, number, date, select, multi_select, user, users
    is_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    default_value: Mapped[Any | None] = mapped_column(
        JSON,
        nullable=True,
    )
    options: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
    )  # For select/multi_select types

    # Relationships
    project = relationship(
        "ProjectModel",
        back_populates="custom_fields",
    )
    values = relationship(
        "CustomFieldValueModel",
        back_populates="custom_field",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<CustomField(id={self.id}, name={self.name}, type={self.type})>"


class CustomFieldValueModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Custom field value database model."""

    __tablename__ = "custom_field_values"

    custom_field_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("custom_fields.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    issue_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    value: Mapped[Any] = mapped_column(
        JSON,
        nullable=False,
    )  # Can be str, int, float, date, list, etc.

    # Relationships
    custom_field = relationship(
        "CustomFieldModel",
        back_populates="values",
    )
    issue = relationship(
        "IssueModel",
        back_populates="custom_field_values",
    )

    def __repr__(self) -> str:
        return (
            f"<CustomFieldValue(id={self.id}, "
            f"custom_field_id={self.custom_field_id}, "
            f"issue_id={self.issue_id})>"
        )
