"""Page and Space database models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class SpaceModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Space database model.
    
    Spaces are containers for documentation pages within an organization.
    Similar to Confluence spaces.
    """

    __tablename__ = "spaces"
    __table_args__ = (
        UniqueConstraint("organization_id", "key", name="uq_space_key"),
    )

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
    key: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )  # e.g., "DOC", "WIKI"
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    settings: Mapped[str | None] = mapped_column(
        Text,  # Store as JSON string
        nullable=True,
    )

    # Relationships
    organization = relationship(
        "OrganizationModel",
        back_populates="spaces",
    )
    pages = relationship(
        "PageModel",
        back_populates="space",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Space(id={self.id}, key={self.key}, name={self.name})>"


class PageModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Page database model.
    
    Pages are documentation entries within a space.
    Supports hierarchical structure via parent_id.
    """

    __tablename__ = "pages"

    space_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("spaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Hierarchy
    parent_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Content
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # Rich text content (HTML, Markdown, or JSON)
    
    # Authorship
    created_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Position in tree
    position: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    # Relationships
    space = relationship(
        "SpaceModel",
        back_populates="pages",
    )
    parent = relationship(
        "PageModel",
        remote_side="PageModel.id",
        back_populates="children",
    )
    children = relationship(
        "PageModel",
        back_populates="parent",
        lazy="selectin",
    )
    comments = relationship(
        "CommentModel",
        back_populates="page",
        foreign_keys="CommentModel.page_id",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    attachments = relationship(
        "AttachmentModel",
        primaryjoin="and_(PageModel.id==foreign(AttachmentModel.entity_id), "
                    "AttachmentModel.entity_type=='page')",
        lazy="selectin",
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f"<Page(id={self.id}, title={self.title[:30]}, space={self.space_id})>"

