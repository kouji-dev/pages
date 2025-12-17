"""SQLAlchemy implementation of IssueLinkRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.issue_link import IssueLink
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.issue_link_repository import IssueLinkRepository
from src.infrastructure.database.models.issue_link import IssueLinkModel


class SQLAlchemyIssueLinkRepository(IssueLinkRepository):
    """SQLAlchemy implementation of IssueLinkRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    async def create(self, link: IssueLink) -> IssueLink:
        """Create a new issue link in the database."""
        model = IssueLinkModel(
            id=link.id,
            source_issue_id=link.source_issue_id,
            target_issue_id=link.target_issue_id,
            link_type=link.link_type,
            created_at=link.created_at,
            updated_at=link.updated_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, link_id: UUID) -> IssueLink | None:
        """Get issue link by ID."""
        result = await self._session.execute(
            select(IssueLinkModel).where(IssueLinkModel.id == link_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_issue_id(self, issue_id: UUID) -> list[IssueLink]:
        """Get all links for an issue (both as source and target)."""
        outgoing = await self.get_outgoing_links(issue_id)
        incoming = await self.get_incoming_links(issue_id)
        return outgoing + incoming

    async def get_outgoing_links(self, issue_id: UUID) -> list[IssueLink]:
        """Get outgoing links from an issue."""
        result = await self._session.execute(
            select(IssueLinkModel).where(IssueLinkModel.source_issue_id == issue_id)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_incoming_links(self, issue_id: UUID) -> list[IssueLink]:
        """Get incoming links to an issue."""
        result = await self._session.execute(
            select(IssueLinkModel).where(IssueLinkModel.target_issue_id == issue_id)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def delete(self, link_id: UUID) -> None:
        """Delete an issue link."""
        result = await self._session.execute(
            select(IssueLinkModel).where(IssueLinkModel.id == link_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("IssueLink", str(link_id))

        await self._session.delete(model)
        await self._session.flush()

    async def exists(self, source_issue_id: UUID, target_issue_id: UUID, link_type: str) -> bool:
        """Check if a link exists."""
        result = await self._session.execute(
            select(IssueLinkModel).where(
                IssueLinkModel.source_issue_id == source_issue_id,
                IssueLinkModel.target_issue_id == target_issue_id,
                IssueLinkModel.link_type == link_type,
            )
        )
        return result.scalar_one_or_none() is not None

    async def check_circular_dependency(self, source_issue_id: UUID, target_issue_id: UUID) -> bool:
        """Check if creating a link would create a circular dependency."""
        # Simple check: if target can reach source through links, it's circular
        # For now, we'll do a basic check - can be enhanced with graph traversal
        visited: set[UUID] = {source_issue_id}
        to_check: list[UUID] = [target_issue_id]

        while to_check:
            current = to_check.pop(0)
            if current in visited:
                return True  # Circular dependency found

            visited.add(current)

            # Get all outgoing links from current issue
            result = await self._session.execute(
                select(IssueLinkModel).where(IssueLinkModel.source_issue_id == current)
            )
            links = result.scalars().all()

            for link in links:
                if link.target_issue_id == source_issue_id:
                    return True  # Direct circular dependency
                if link.target_issue_id not in visited:
                    to_check.append(link.target_issue_id)

        return False

    def _to_entity(self, model: IssueLinkModel) -> IssueLink:
        """Convert IssueLinkModel to IssueLink entity."""
        return IssueLink(
            id=model.id,
            source_issue_id=model.source_issue_id,
            target_issue_id=model.target_issue_id,
            link_type=model.link_type,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
