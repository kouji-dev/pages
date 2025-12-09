"""Search query service for issues and pages."""

from collections.abc import Iterable
from typing import Any
from uuid import UUID

from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import IssueModel, PageModel


class SearchQueryService:
    """Provides simple search capabilities over issues and pages."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search_issues(
        self,
        query: str,
        project_id: UUID,
        skip: int,
        limit: int,
        assignee_id: UUID | None = None,
        reporter_id: UUID | None = None,
        status: str | None = None,
        type: str | None = None,
        priority: str | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """Search issues by title/description with basic scoring (length-based fallback)."""

        search_pattern = f"%{query}%"
        conditions: list[Any] = [
            IssueModel.project_id == project_id,
            IssueModel.deleted_at.is_(None),
            or_(
                IssueModel.title.ilike(search_pattern),
                IssueModel.description.ilike(search_pattern),
            ),
        ]

        if assignee_id:
            conditions.append(IssueModel.assignee_id == assignee_id)
        if reporter_id:
            conditions.append(IssueModel.reporter_id == reporter_id)
        if status:
            conditions.append(IssueModel.status == status)
        if type:
            conditions.append(IssueModel.type == type)
        if priority:
            conditions.append(IssueModel.priority == priority)

        # Count total
        count_stmt = select(func.count()).select_from(IssueModel).where(*conditions)
        count_result = await self._session.execute(count_stmt)
        total: int = count_result.scalar_one()

        # Simple score: length of title match + description match
        score_expr = func.coalesce(func.length(IssueModel.title), 0) + func.coalesce(
            func.length(IssueModel.description), 0
        )

        stmt = (
            select(
                IssueModel.id,
                IssueModel.title,
                IssueModel.project_id,
                score_expr.label("score"),
                func.substr(IssueModel.description, 1, 200).label("snippet"),
            )
            .where(*conditions)
            .order_by(text("score DESC"), IssueModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        rows = result.mappings().all()
        items = [
            {
                "entity_type": "issue",
                "id": row["id"],
                "title": row["title"],
                "snippet": row["snippet"],
                "score": float(row["score"] or 0),
                "project_id": row["project_id"],
                "space_id": None,
            }
            for row in rows
        ]

        return items, total

    async def search_pages(
        self,
        query: str,
        space_id: UUID,
        skip: int,
        limit: int,
    ) -> tuple[list[dict[str, Any]], int]:
        """Search pages by title/content."""

        search_pattern = f"%{query}%"
        conditions: list[Any] = [
            PageModel.space_id == space_id,
            PageModel.deleted_at.is_(None),
            or_(
                PageModel.title.ilike(search_pattern),
                PageModel.content.ilike(search_pattern),
            ),
        ]

        count_stmt = select(func.count()).select_from(PageModel).where(*conditions)
        count_result = await self._session.execute(count_stmt)
        total: int = count_result.scalar_one()

        score_expr = func.coalesce(func.length(PageModel.title), 0) + func.coalesce(
            func.length(PageModel.content), 0
        )

        stmt = (
            select(
                PageModel.id,
                PageModel.title,
                PageModel.space_id,
                score_expr.label("score"),
                func.substr(PageModel.content, 1, 200).label("snippet"),
            )
            .where(*conditions)
            .order_by(text("score DESC"), PageModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        rows = result.mappings().all()
        items = [
            {
                "entity_type": "page",
                "id": row["id"],
                "title": row["title"],
                "snippet": row["snippet"],
                "score": float(row["score"] or 0),
                "project_id": None,
                "space_id": row["space_id"],
            }
            for row in rows
        ]

        return items, total

    @staticmethod
    def _merge_and_paginate(
        issue_items: Iterable[dict[str, Any]],
        page_items: Iterable[dict[str, Any]],
        skip: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Merge two result sets (already scored) and paginate."""

        combined = list(issue_items) + list(page_items)
        combined.sort(key=lambda x: (x.get("score", 0),), reverse=True)
        return combined[skip : skip + limit]
