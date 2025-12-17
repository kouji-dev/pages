"""List nodes use case."""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.node import NodeListResponse, NodeListItemResponse
from src.domain.repositories import ProjectRepository, SpaceRepository
from src.infrastructure.database.models import (
    IssueModel,
    PageModel,
    ProjectMemberModel,
    ProjectModel,
    SpaceModel,
)

logger = structlog.get_logger()


class ListNodesUseCase:
    """Use case for listing nodes (projects + spaces) in an organization."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        space_repository: SpaceRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            project_repository: Project repository
            space_repository: Space repository
            session: Database session for getting folder_id and counts
        """
        self._project_repository = project_repository
        self._space_repository = space_repository
        self._session = session

    async def execute(
        self,
        organization_id: str,
        folder_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> NodeListResponse:
        """Execute list nodes.

        Args:
            organization_id: Organization UUID
            folder_id: Optional folder UUID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Node list response DTO
        """
        org_uuid = UUID(organization_id)
        folder_uuid = UUID(folder_id) if folder_id else None

        logger.info(
            "Listing nodes",
            organization_id=organization_id,
            folder_id=folder_id,
            skip=skip,
            limit=limit,
        )

        # Get projects and spaces
        projects = await self._project_repository.get_all(
            organization_id=org_uuid,
            folder_id=folder_uuid,
            skip=skip,
            limit=limit,
            include_deleted=False,
        )

        spaces = await self._space_repository.get_all(
            organization_id=org_uuid,
            folder_id=folder_uuid,
            skip=skip,
            limit=limit,
            include_deleted=False,
        )

        # Combine into nodes
        node_responses = []

        # Add projects as nodes
        for project in projects:
            # Get folder_id from model
            result = await self._session.execute(
                select(ProjectModel.folder_id).where(ProjectModel.id == project.id)
            )
            project_folder_id = result.scalar_one_or_none()

            # Count members
            result = await self._session.execute(
                select(func.count())
                .select_from(ProjectMemberModel)
                .where(ProjectMemberModel.project_id == project.id)
            )
            member_count: int = result.scalar_one()

            # Count issues
            result = await self._session.execute(
                select(func.count())
                .select_from(IssueModel)
                .where(IssueModel.project_id == project.id)
            )
            issue_count: int = result.scalar_one()

            node_responses.append(
                NodeListItemResponse(
                    type="project",
                    id=project.id,
                    organization_id=project.organization_id,
                    name=project.name,
                    key=project.key,
                    description=project.description,
                    folder_id=project_folder_id,
                    member_count=member_count,
                    issue_count=issue_count,
                    page_count=None,
                )
            )

        # Add spaces as nodes
        for space in spaces:
            # Get folder_id from model
            result = await self._session.execute(
                select(SpaceModel.folder_id).where(SpaceModel.id == space.id)
            )
            space_folder_id = result.scalar_one_or_none()

            # Count pages
            result = await self._session.execute(
                select(func.count()).select_from(PageModel).where(PageModel.space_id == space.id)
            )
            page_count: int = result.scalar_one()

            node_responses.append(
                NodeListItemResponse(
                    type="space",
                    id=space.id,
                    organization_id=space.organization_id,
                    name=space.name,
                    key=space.key,
                    description=space.description,
                    folder_id=space_folder_id,
                    member_count=None,
                    issue_count=None,
                    page_count=page_count,
                )
            )

        total = len(node_responses)

        logger.info("Nodes listed", count=total, organization_id=organization_id)

        return NodeListResponse(nodes=node_responses, total=total)
