"""Macro database model."""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class MacroModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Macro database model.

    Macros are reusable content blocks that can be embedded in pages.
    """

    __tablename__ = "macros"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )
    code: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )  # Macro code/implementation
    config_schema: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # JSON schema for macro configuration
    macro_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # table, code_block, info_panel, page_tree, issue_embed
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )  # Whether this is a system macro (cannot be deleted)

    def __repr__(self) -> str:
        return f"<Macro(id={self.id}, name={self.name}, type={self.macro_type})>"
