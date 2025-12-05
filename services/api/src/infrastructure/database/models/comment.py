"""Comment database model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class CommentModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Comment database model.
    
    Comments can be attached to issues or pages.
    Uses polymorphic association pattern.
    """

    __tablename__ = "comments"

    # Polymorphic association
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # 'issue' or 'page'
    entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    
    # For direct foreign key to issue (optional, for performance)
    issue_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    # For direct foreign key to page (optional, for performance)
    page_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    # Author
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Content
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    # Edit tracking
    is_edited: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    user = relationship(
        "UserModel",
        back_populates="comments",
    )
    issue = relationship(
        "IssueModel",
        back_populates="comments",
        foreign_keys=[issue_id],
    )
    page = relationship(
        "PageModel",
        back_populates="comments",
        foreign_keys=[page_id],
    )

    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, entity_type={self.entity_type}, user={self.user_id})>"

