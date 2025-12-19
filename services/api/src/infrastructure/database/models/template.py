"""Template database model."""

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class TemplateModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Template database model.

    Templates are pre-defined content structures for creating pages.
    """

    __tablename__ = "templates"

    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # Template category
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # Template content (HTML or Markdown)
    is_default: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    created_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    organization = relationship(
        "OrganizationModel",
        back_populates="templates",
    )

    def __repr__(self) -> str:
        return f"<Template(id={self.id}, name={self.name}, organization_id={self.organization_id})>"
