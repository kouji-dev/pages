"""Page version database model."""

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class PageVersionModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Page version database model.

    Stores historical versions of pages for version history and restoration.
    """

    __tablename__ = "page_versions"
    __table_args__ = ({"comment": "Stores historical versions of pages for version history"},)

    page_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    page = relationship(
        "PageModel",
        back_populates="versions",
    )
    creator = relationship(
        "UserModel",
        foreign_keys=[created_by],
    )

    def __repr__(self) -> str:
        return f"<PageVersion(id={self.id}, page_id={self.page_id}, version={self.version_number})>"
