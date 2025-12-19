"""SQLAlchemy implementation of MacroRepository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Macro
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import MacroRepository
from src.infrastructure.database.models import MacroModel


class SQLAlchemyMacroRepository(MacroRepository):
    """SQLAlchemy implementation of MacroRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, macro: Macro) -> Macro:
        """Create a new macro in the database."""
        model = MacroModel(
            id=macro.id,
            name=macro.name,
            code=macro.code,
            config_schema=macro.config_schema,
            macro_type=macro.macro_type,
            is_system=macro.is_system,
            created_at=macro.created_at,
            updated_at=macro.updated_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, macro_id: UUID) -> Macro | None:
        """Get macro by ID."""
        result = await self._session.execute(select(MacroModel).where(MacroModel.id == macro_id))
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_name(self, name: str) -> Macro | None:
        """Get macro by name."""
        result = await self._session.execute(select(MacroModel).where(MacroModel.name == name))
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        macro_type: str | None = None,
        include_system: bool = True,
    ) -> list[Macro]:
        """Get all macros with pagination."""
        query = select(MacroModel)

        if macro_type:
            query = query.where(MacroModel.macro_type == macro_type)

        if not include_system:
            query = query.where(MacroModel.is_system == False)  # noqa: E712

        query = query.offset(skip).limit(limit).order_by(MacroModel.name)

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count(
        self,
        macro_type: str | None = None,
        include_system: bool = True,
    ) -> int:
        """Count total macros."""
        query = select(func.count(MacroModel.id))

        if macro_type:
            query = query.where(MacroModel.macro_type == macro_type)

        if not include_system:
            query = query.where(MacroModel.is_system == False)  # noqa: E712

        result = await self._session.execute(query)
        return result.scalar_one() or 0

    async def update(self, macro: Macro) -> Macro:
        """Update an existing macro."""
        result = await self._session.execute(select(MacroModel).where(MacroModel.id == macro.id))
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Macro", str(macro.id))

        model.name = macro.name
        model.code = macro.code
        model.config_schema = macro.config_schema
        model.macro_type = macro.macro_type
        model.updated_at = macro.updated_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, macro_id: UUID) -> None:
        """Delete a macro."""
        result = await self._session.execute(select(MacroModel).where(MacroModel.id == macro_id))
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Macro", str(macro_id))

        if model.is_system:
            raise ValueError("Cannot delete system macro")

        await self._session.delete(model)
        await self._session.flush()

    def _to_entity(self, model: MacroModel) -> Macro:
        """Convert database model to domain entity."""
        return Macro(
            id=model.id,
            name=model.name,
            code=model.code,
            config_schema=model.config_schema,
            macro_type=model.macro_type,
            is_system=model.is_system,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
