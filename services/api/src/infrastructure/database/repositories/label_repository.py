"""SQLAlchemy implementation of LabelRepository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Label
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import LabelRepository
from src.infrastructure.database.models import IssueLabelModel, IssueModel, LabelModel


class SQLAlchemyLabelRepository(LabelRepository):
    """SQLAlchemy implementation of LabelRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    async def create(self, label: Label) -> Label:
        """Create a new label in the database."""
        if await self.exists_by_name(label.project_id, label.name):
            raise ConflictException(
                f"Label with name '{label.name}' already exists in this project",
                field="name",
            )
        model = LabelModel(
            id=label.id,
            project_id=label.project_id,
            name=label.name,
            color=label.color,
            description=label.description,
            created_at=label.created_at,
            updated_at=label.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, label_id: UUID) -> Label | None:
        """Get label by ID."""
        result = await self._session.execute(select(LabelModel).where(LabelModel.id == label_id))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def get_by_project(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
    ) -> list[Label]:
        """Get labels for a project with optional pagination and search."""
        query = select(LabelModel).where(LabelModel.project_id == project_id)
        if search and search.strip():
            query = query.where(LabelModel.name.ilike(f"%{search.strip()}%"))
        query = query.offset(skip).limit(limit).order_by(LabelModel.name)
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def count_by_project(
        self,
        project_id: UUID,
        search: str | None = None,
    ) -> int:
        """Count labels in a project."""
        query = (
            select(func.count()).select_from(LabelModel).where(LabelModel.project_id == project_id)
        )
        if search and search.strip():
            query = query.where(LabelModel.name.ilike(f"%{search.strip()}%"))
        result = await self._session.execute(query)
        return int(result.scalar_one())

    async def exists_by_name(
        self, project_id: UUID, name: str, exclude_id: UUID | None = None
    ) -> bool:
        """Check if label with name exists in project."""
        query = select(LabelModel).where(
            LabelModel.project_id == project_id,
            LabelModel.name == name.strip(),
        )
        if exclude_id:
            query = query.where(LabelModel.id != exclude_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none() is not None

    async def update(self, label: Label) -> Label:
        """Update an existing label."""
        result = await self._session.execute(select(LabelModel).where(LabelModel.id == label.id))
        model = result.scalar_one_or_none()
        if model is None:
            raise EntityNotFoundException("Label", str(label.id))
        if await self.exists_by_name(label.project_id, label.name, exclude_id=label.id):
            raise ConflictException(
                f"Label with name '{label.name}' already exists in this project",
                field="name",
            )
        model.name = label.name
        model.color = label.color
        model.description = label.description
        model.updated_at = label.updated_at
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, label_id: UUID) -> None:
        """Delete a label (cascade to issue_labels)."""
        result = await self._session.execute(select(LabelModel).where(LabelModel.id == label_id))
        model = result.scalar_one_or_none()
        if model is None:
            raise EntityNotFoundException("Label", str(label_id))
        await self._session.delete(model)
        await self._session.flush()

    async def add_label_to_issue(self, issue_id: UUID, label_id: UUID) -> None:
        """Add a label to an issue."""
        # Verify issue exists
        issue_result = await self._session.execute(
            select(IssueModel).where(IssueModel.id == issue_id)
        )
        if issue_result.scalar_one_or_none() is None:
            raise EntityNotFoundException("Issue", str(issue_id))
        # Verify label exists
        label_result = await self._session.execute(
            select(LabelModel).where(LabelModel.id == label_id)
        )
        if label_result.scalar_one_or_none() is None:
            raise EntityNotFoundException("Label", str(label_id))
        if await self.issue_has_label(issue_id, label_id):
            raise ConflictException(
                "Issue already has this label",
                field="label_id",
            )
        link = IssueLabelModel(issue_id=issue_id, label_id=label_id)
        self._session.add(link)
        await self._session.flush()

    async def remove_label_from_issue(self, issue_id: UUID, label_id: UUID) -> None:
        """Remove a label from an issue."""
        result = await self._session.execute(
            select(IssueLabelModel).where(
                IssueLabelModel.issue_id == issue_id,
                IssueLabelModel.label_id == label_id,
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise EntityNotFoundException(
                "IssueLabel",
                f"issue_id={issue_id}, label_id={label_id}",
            )
        await self._session.delete(model)
        await self._session.flush()

    async def get_labels_for_issue(self, issue_id: UUID) -> list[Label]:
        """Get all labels for an issue."""
        query = (
            select(LabelModel)
            .join(IssueLabelModel, IssueLabelModel.label_id == LabelModel.id)
            .where(IssueLabelModel.issue_id == issue_id)
        )
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def issue_has_label(self, issue_id: UUID, label_id: UUID) -> bool:
        """Check if an issue has a specific label."""
        result = await self._session.execute(
            select(IssueLabelModel).where(
                IssueLabelModel.issue_id == issue_id,
                IssueLabelModel.label_id == label_id,
            )
        )
        return result.scalar_one_or_none() is not None

    def _to_entity(self, model: LabelModel) -> Label:
        """Convert LabelModel to Label entity."""
        return Label(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            color=model.color,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
