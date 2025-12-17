"""List issue links use case."""

from uuid import UUID

import structlog

from src.application.dtos.issue_link import IssueLinkListResponse, IssueLinkResponse
from src.domain.repositories.issue_link_repository import IssueLinkRepository

logger = structlog.get_logger()


class ListIssueLinksUseCase:
    """Use case for listing issue links."""

    def __init__(self, issue_link_repository: IssueLinkRepository) -> None:
        """Initialize use case with dependencies."""
        self._issue_link_repository = issue_link_repository

    async def execute(self, issue_id: UUID) -> IssueLinkListResponse:
        """Execute list issue links."""
        logger.info("Listing issue links", issue_id=str(issue_id))

        links = await self._issue_link_repository.get_by_issue_id(issue_id)

        link_items = [
            IssueLinkResponse.model_validate(
                {
                    "id": link.id,
                    "source_issue_id": link.source_issue_id,
                    "target_issue_id": link.target_issue_id,
                    "link_type": link.link_type,
                    "created_at": link.created_at,
                    "updated_at": link.updated_at,
                }
            )
            for link in links
        ]

        return IssueLinkListResponse(links=link_items, total=len(link_items))
