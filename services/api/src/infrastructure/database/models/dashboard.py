"""Dashboard database models."""

from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class DashboardModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Dashboard database model."""

    __tablename__ = "dashboards"

    project_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    layout: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Relationships
    project = relationship(
        "ProjectModel",
        back_populates="dashboards",
    )
    user = relationship(
        "UserModel",
        back_populates="dashboards",
    )
    widgets = relationship(
        "DashboardWidgetModel",
        back_populates="dashboard",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="DashboardWidgetModel.position",
    )

    def __repr__(self) -> str:
        return f"<Dashboard(id={self.id}, name={self.name})>"


class DashboardWidgetModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Dashboard widget database model."""

    __tablename__ = "dashboard_widgets"

    dashboard_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("dashboards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    config: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Relationships
    dashboard = relationship(
        "DashboardModel",
        back_populates="widgets",
    )

    def __repr__(self) -> str:
        return (
            f"<DashboardWidget(id={self.id}, type={self.type}, dashboard_id={self.dashboard_id})>"
        )
