"""Organization database models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class OrganizationModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Organization database model.
    
    Organizations are the top-level containers for projects and spaces.
    """

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    settings: Mapped[str | None] = mapped_column(
        Text,  # Store as JSON string
        nullable=True,
    )

    # Relationships
    members = relationship(
        "OrganizationMemberModel",
        back_populates="organization",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    projects = relationship(
        "ProjectModel",
        back_populates="organization",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    spaces = relationship(
        "SpaceModel",
        back_populates="organization",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"


class OrganizationMemberModel(Base, TimestampMixin):
    """Organization member association model.
    
    Links users to organizations with roles.
    """

    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_member"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="member",
    )  # admin, member, viewer

    # Relationships
    organization = relationship(
        "OrganizationModel",
        back_populates="members",
    )
    user = relationship(
        "UserModel",
        back_populates="organization_memberships",
    )

    def __repr__(self) -> str:
        return f"<OrganizationMember(org={self.organization_id}, user={self.user_id}, role={self.role})>"

