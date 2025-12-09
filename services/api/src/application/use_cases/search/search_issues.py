"""Use case for searching issues."""

from uuid import UUID

from src.application.dtos.search import SearchIssuesResponse, SearchResultItem
from src.application.services.search_query_service import SearchQueryService


class SearchIssuesUseCase:
    """Search issues within a project."""

    DEFAULT_LIMIT = 20
    MAX_LIMIT = 50

    def __init__(self, search_service: SearchQueryService) -> None:
        self._search_service = search_service

    async def execute(
        self,
        project_id: UUID,
        query: str,
        page: int = 1,
        limit: int = DEFAULT_LIMIT,
        assignee_id: UUID | None = None,
        reporter_id: UUID | None = None,
        status: str | None = None,
        type: str | None = None,
        priority: str | None = None,
    ) -> SearchIssuesResponse:
        if page < 1:
            raise ValueError("Page must be >= 1")
        if limit < 1:
            raise ValueError("Limit must be >= 1")
        if limit > self.MAX_LIMIT:
            limit = self.MAX_LIMIT

        skip = (page - 1) * limit

        items_raw, total = await self._search_service.search_issues(
            query=query,
            project_id=project_id,
            skip=skip,
            limit=limit,
            assignee_id=assignee_id,
            reporter_id=reporter_id,
            status=status,
            type=type,
            priority=priority,
        )

        items = [
            SearchResultItem(
                entity_type="issue",
                id=item["id"],
                title=item["title"],
                snippet=item.get("snippet"),
                score=item.get("score", 0.0),
                project_id=item.get("project_id"),
                space_id=None,
            )
            for item in items_raw
        ]

        return SearchIssuesResponse(items=items, total=total, page=page, limit=limit)
