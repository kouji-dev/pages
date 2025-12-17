"""Issue link database model."""

from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class IssueLinkModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Issue link database model."""

    __tablename__ = "issue_links"

    source_issue_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_issue_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    link_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # Relationships
    source_issue = relationship(
        "IssueModel",
        foreign_keys=[source_issue_id],
        back_populates="outgoing_links",
    )
    target_issue = relationship(
        "IssueModel",
        foreign_keys=[target_issue_id],
        back_populates="incoming_links",
    )

    def __repr__(self) -> str:
        return (
            f"<IssueLink(id={self.id}, "
            f"source={self.source_issue_id}, "
            f"target={self.target_issue_id}, "
            f"type={self.link_type})>"
        )
