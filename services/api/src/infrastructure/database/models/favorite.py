"""Favorite database models."""

from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class FavoriteModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Favorite database model.

    Favorites are heterogeneous - they can reference projects, spaces, or pages.
    """

    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "entity_type", "entity_id", name="uq_favorite"),)

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )  # "project", "space", "page" - uses EntityType value object constants
    entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Relationships
    user = relationship(
        "UserModel",
        back_populates="favorites",
    )

    def __repr__(self) -> str:
        return f"<Favorite(id={self.id}, user_id={self.user_id}, entity_type={self.entity_type}, entity_id={self.entity_id})>"
