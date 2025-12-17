"""Folder database models."""

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class FolderModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Folder database model.

    Folders are logical containers for organizing projects and spaces within an organization.
    They support hierarchical structure via parent_id.
    """

    __tablename__ = "folders"

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
    parent_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("folders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Relationships
    organization = relationship(
        "OrganizationModel",
        back_populates="folders",
    )
    parent = relationship(
        "FolderModel",
        remote_side="FolderModel.id",
        back_populates="children",
    )
    children = relationship(
        "FolderModel",
        back_populates="parent",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Folder(id={self.id}, name={self.name}, organization_id={self.organization_id})>"

