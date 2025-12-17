"""Delete issue link use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.issue_link_repository import IssueLinkRepository

logger = structlog.get_logger()


class DeleteIssueLinkUseCase:
    """Use case for deleting an issue link."""

    def __init__(self, issue_link_repository: IssueLinkRepository) -> None:
        """Initialize use case with dependencies."""
        self._issue_link_repository = issue_link_repository

    async def execute(self, link_id: UUID) -> None:
        """Execute delete issue link."""
        logger.info("Deleting issue link", link_id=str(link_id))

        link = await self._issue_link_repository.get_by_id(link_id)
        if link is None:
            logger.warning("Issue link not found", link_id=str(link_id))
            raise EntityNotFoundException("IssueLink", str(link_id))

        await self._issue_link_repository.delete(link_id)

        logger.info("Issue link deleted", link_id=str(link_id))
