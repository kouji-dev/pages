"""Organization invitation database model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class InvitationModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Organization invitation database model.

    Stores invitations sent to users to join organizations.
    """

    __tablename__ = "invitations"
    __table_args__ = (
        UniqueConstraint("organization_id", "email", "token", name="uq_org_email_token"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="member",
    )  # admin, member, viewer
    invited_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    organization = relationship(
        "OrganizationModel",
        back_populates="invitations",
    )
    inviter = relationship(
        "UserModel",
        foreign_keys=[invited_by],
    )

    def __repr__(self) -> str:
        return f"<Invitation(id={self.id}, org={self.organization_id}, email={self.email}, token={self.token[:10]}...)>"

