"""Create issue link use case."""

from uuid import UUID

import structlog

from src.application.dtos.issue_link import CreateIssueLinkRequest, IssueLinkResponse
from src.domain.entities.issue_link import IssueLink
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import IssueRepository
from src.domain.repositories.issue_link_repository import IssueLinkRepository

logger = structlog.get_logger()


class CreateIssueLinkUseCase:
    """Use case for creating an issue link."""

    def __init__(
        self,
        issue_link_repository: IssueLinkRepository,
        issue_repository: IssueRepository,
    ) -> None:
        """Initialize use case with dependencies."""
        self._issue_link_repository = issue_link_repository
        self._issue_repository = issue_repository

    async def execute(
        self, source_issue_id: UUID, request: CreateIssueLinkRequest
    ) -> IssueLinkResponse:
        """Execute create issue link."""
        logger.info(
            "Creating issue link",
            source_issue_id=str(source_issue_id),
            target_issue_id=str(request.target_issue_id),
            link_type=request.link_type,
        )

        # Verify both issues exist
        source_issue = await self._issue_repository.get_by_id(source_issue_id)
        if source_issue is None:
            logger.warning("Source issue not found", issue_id=str(source_issue_id))
            raise EntityNotFoundException("Issue", str(source_issue_id))

        target_issue = await self._issue_repository.get_by_id(request.target_issue_id)
        if target_issue is None:
            logger.warning("Target issue not found", issue_id=str(request.target_issue_id))
            raise EntityNotFoundException("Issue", str(request.target_issue_id))

        # Check for circular dependency
        if await self._issue_link_repository.check_circular_dependency(
            source_issue_id, request.target_issue_id
        ):
            raise ValidationException(
                "Creating this link would create a circular dependency", field="link"
            )

        # Check if link already exists
        if await self._issue_link_repository.exists(
            source_issue_id, request.target_issue_id, request.link_type
        ):
            raise ValidationException(
                f"Link of type '{request.link_type}' already exists between these issues",
                field="link",
            )

        # Create issue link entity
        try:
            issue_link = IssueLink.create(
                source_issue_id=source_issue_id,
                target_issue_id=request.target_issue_id,
                link_type=request.link_type,
            )
        except ValueError as e:
            raise ValidationException(str(e), field="link") from e

        # Save to database
        created_link = await self._issue_link_repository.create(issue_link)

        logger.info("Issue link created", link_id=str(created_link.id))

        return IssueLinkResponse.model_validate(
            {
                "id": created_link.id,
                "source_issue_id": created_link.source_issue_id,
                "target_issue_id": created_link.target_issue_id,
                "link_type": created_link.link_type,
                "created_at": created_link.created_at,
                "updated_at": created_link.updated_at,
            }
        )
