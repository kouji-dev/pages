"""Get project summary statistics use case."""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.project_reports import ProjectSummaryStatsResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import ProjectRepository, SprintRepository
from src.infrastructure.database.models import (
    IssueModel,
    ProjectMemberModel,
    SprintIssueModel,
    SprintModel,
)

logger = structlog.get_logger()


class GetProjectSummaryStatsUseCase:
    """Use case for getting project summary statistics."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        sprint_repository: SprintRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            project_repository: Project repository
            sprint_repository: Sprint repository
            session: Database session
        """
        self._project_repository = project_repository
        self._sprint_repository = sprint_repository
        self._session = session

    async def execute(self, project_id: UUID) -> ProjectSummaryStatsResponse:
        """Execute getting project summary statistics.

        Args:
            project_id: Project UUID

        Returns:
            Project summary stats response DTO

        Raises:
            EntityNotFoundException: If project not found
        """
        logger.info("Getting project summary stats", project_id=str(project_id))

        # Verify project exists
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            logger.warning("Project not found", project_id=str(project_id))
            raise EntityNotFoundException("Project", str(project_id))

        # Count team members
        members_result = await self._session.execute(
            select(func.count())
            .select_from(ProjectMemberModel)
            .where(ProjectMemberModel.project_id == project_id)
        )
        team_members = int(members_result.scalar_one() or 0)

        # Calculate average velocity from completed sprints
        completed_sprints_result = await self._session.execute(
            select(SprintModel)
            .where(SprintModel.project_id == project_id)
            .where(SprintModel.status == "completed")
            .order_by(SprintModel.start_date.asc())
        )
        completed_sprints = completed_sprints_result.scalars().all()

        velocities: list[int] = []
        for sprint in completed_sprints:
            # Get sprint issues
            sprint_issues_result = await self._session.execute(
                select(SprintIssueModel.issue_id)
                .where(SprintIssueModel.sprint_id == sprint.id)
            )
            issue_ids = [row[0] for row in sprint_issues_result.all()]

            if issue_ids:
                # Get completed story points
                completed_result = await self._session.execute(
                    select(func.coalesce(func.sum(IssueModel.story_points), 0))
                    .where(IssueModel.id.in_(issue_ids))
                    .where(IssueModel.status == "done")
                    .where(IssueModel.deleted_at.is_(None))
                )
                completed = int(completed_result.scalar_one() or 0)
                if completed > 0:
                    velocities.append(completed)

        avg_velocity = sum(velocities) / len(velocities) if velocities else 0.0

        # Calculate average cycle time (simplified: time from creation to completion)
        # For issues that are done, calculate average days between created_at and updated_at
        cycle_times_result = await self._session.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        IssueModel.updated_at - IssueModel.created_at,
                    )
                    / 86400.0  # Convert to days
                )
            )
            .select_from(IssueModel)
            .where(IssueModel.project_id == project_id)
            .where(IssueModel.status == "done")
            .where(IssueModel.deleted_at.is_(None))
            .where(IssueModel.created_at.isnot(None))
            .where(IssueModel.updated_at.isnot(None))
        )
        avg_cycle_time = float(cycle_times_result.scalar_one() or 0.0)

        # Get current sprint goal completion
        active_sprint_result = await self._session.execute(
            select(SprintModel)
            .where(SprintModel.project_id == project_id)
            .where(SprintModel.status == "active")
            .order_by(SprintModel.start_date.desc())
            .limit(1)
        )
        active_sprint = active_sprint_result.scalar_one_or_none()

        sprint_goal_completion = 0.0
        if active_sprint:
            # Get sprint issues
            sprint_issues_result = await self._session.execute(
                select(SprintIssueModel.issue_id)
                .where(SprintIssueModel.sprint_id == active_sprint.id)
            )
            issue_ids = [row[0] for row in sprint_issues_result.all()]

            if issue_ids:
                # Get total and completed story points
                total_result = await self._session.execute(
                    select(func.coalesce(func.sum(IssueModel.story_points), 0))
                    .where(IssueModel.id.in_(issue_ids))
                    .where(IssueModel.deleted_at.is_(None))
                )
                total = int(total_result.scalar_one() or 0)

                completed_result = await self._session.execute(
                    select(func.coalesce(func.sum(IssueModel.story_points), 0))
                    .where(IssueModel.id.in_(issue_ids))
                    .where(IssueModel.status == "done")
                    .where(IssueModel.deleted_at.is_(None))
                )
                completed = int(completed_result.scalar_one() or 0)

                if total > 0:
                    sprint_goal_completion = (completed / total) * 100.0

        return ProjectSummaryStatsResponse(
            project_id=project_id,
            avg_velocity=round(avg_velocity, 1),
            team_members=team_members,
            cycle_time_days=round(avg_cycle_time, 1),
            sprint_goal_completion=round(sprint_goal_completion, 1),
        )
