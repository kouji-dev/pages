"""Use case for unified search across issues and pages."""

from typing import Literal
from uuid import UUID

from src.application.dtos.search import SearchResponse, SearchResultItem
from src.application.services.search_query_service import SearchQueryService


class SearchAllUseCase:
    """Search across issues and pages."""

    DEFAULT_LIMIT = 20
    MAX_LIMIT = 50

    def __init__(self, search_service: SearchQueryService) -> None:
        self._search_service = search_service

    async def execute(
        self,
        query: str,
        search_type: Literal["all", "issues", "pages"],
        project_id: UUID | None = None,
        space_id: UUID | None = None,
        page: int = 1,
        limit: int = DEFAULT_LIMIT,
        assignee_id: UUID | None = None,
        reporter_id: UUID | None = None,
        status: str | None = None,
        type: str | None = None,
        priority: str | None = None,
    ) -> SearchResponse:
        if page < 1:
            raise ValueError("Page must be >= 1")
        if limit < 1:
            raise ValueError("Limit must be >= 1")
        if limit > self.MAX_LIMIT:
            limit = self.MAX_LIMIT

        skip = (page - 1) * limit

        issue_items: list[dict] = []
        page_items: list[dict] = []
        issue_total = 0
        page_total = 0

        if search_type in ("all", "issues") and project_id:
            issue_items, issue_total = await self._search_service.search_issues(
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

        if search_type in ("all", "pages") and space_id:
            page_items, page_total = await self._search_service.search_pages(
                query=query,
                space_id=space_id,
                skip=skip,
                limit=limit,
            )

        combined = issue_items + page_items
        combined.sort(key=lambda x: x.get("score", 0), reverse=True)
        paginated = combined[skip : skip + limit]

        items = [
            SearchResultItem(
                entity_type=item["entity_type"],
                id=item["id"],
                title=item["title"],
                snippet=item.get("snippet"),
                score=item.get("score", 0.0),
                project_id=item.get("project_id"),
                space_id=item.get("space_id"),
            )
            for item in paginated
        ]

        total = issue_total + page_total

        return SearchResponse(items=items, total=total, page=page, limit=limit)
