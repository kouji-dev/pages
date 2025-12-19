"""Page and space permission database models."""

from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class PagePermissionModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Page permission database model.

    Stores user-specific permissions for pages.
    """

    __tablename__ = "page_permissions"

    page_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # read, edit, delete, admin
    inherited_from_space: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Relationships
    page = relationship(
        "PageModel",
        back_populates="permissions",
    )
    user = relationship(
        "UserModel",
        foreign_keys=[user_id],
    )

    def __repr__(self) -> str:
        return f"<PagePermission(id={self.id}, page_id={self.page_id}, user_id={self.user_id}, role={self.role})>"


class SpacePermissionModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Space permission database model.

    Stores user-specific permissions for spaces.
    """

    __tablename__ = "space_permissions"

    space_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("spaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # view, create, edit, delete, admin

    # Relationships
    space = relationship(
        "SpaceModel",
        back_populates="permissions",
    )
    user = relationship(
        "UserModel",
        foreign_keys=[user_id],
    )

    def __repr__(self) -> str:
        return f"<SpacePermission(id={self.id}, space_id={self.space_id}, user_id={self.user_id}, role={self.role})>"
