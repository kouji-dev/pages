"""Workflow database models."""

from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class WorkflowModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Workflow database model."""

    __tablename__ = "workflows"

    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    # Relationships
    project = relationship(
        "ProjectModel",
        back_populates="workflows",
    )
    statuses = relationship(
        "WorkflowStatusModel",
        back_populates="workflow",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="WorkflowStatusModel.order",
    )
    transitions = relationship(
        "WorkflowTransitionModel",
        back_populates="workflow",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Workflow(id={self.id}, name={self.name}, project_id={self.project_id})>"


class WorkflowStatusModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Workflow status database model."""

    __tablename__ = "workflow_statuses"

    workflow_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    is_initial: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_final: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Relationships
    workflow = relationship(
        "WorkflowModel",
        back_populates="statuses",
    )
    from_transitions = relationship(
        "WorkflowTransitionModel",
        foreign_keys="WorkflowTransitionModel.from_status_id",
        back_populates="from_status",
        lazy="selectin",
    )
    to_transitions = relationship(
        "WorkflowTransitionModel",
        foreign_keys="WorkflowTransitionModel.to_status_id",
        back_populates="to_status",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<WorkflowStatus(id={self.id}, name={self.name}, workflow_id={self.workflow_id})>"


class WorkflowTransitionModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Workflow transition database model."""

    __tablename__ = "workflow_transitions"

    workflow_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_status_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("workflow_statuses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    to_status_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("workflow_statuses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Relationships
    workflow = relationship(
        "WorkflowModel",
        back_populates="transitions",
    )
    from_status = relationship(
        "WorkflowStatusModel",
        foreign_keys=[from_status_id],
        back_populates="from_transitions",
    )
    to_status = relationship(
        "WorkflowStatusModel",
        foreign_keys=[to_status_id],
        back_populates="to_transitions",
    )

    def __repr__(self) -> str:
        return (
            f"<WorkflowTransition(id={self.id}, "
            f"from_status_id={self.from_status_id}, "
            f"to_status_id={self.to_status_id})>"
        )
