"""Unit tests for export use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.domain.entities import Page, Space, User
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects import Email, HashedPassword


@pytest.fixture
def mock_page_repository():
    """Mock page repository."""
    return AsyncMock()


@pytest.fixture
def mock_space_repository():
    """Mock space repository."""
    return AsyncMock()


@pytest.fixture
def test_user():
    """Create a test user."""
    valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
    return User(
        id=uuid4(),
        email=Email("test@example.com"),
        password_hash=HashedPassword(valid_hash),
        name="Test User",
        is_active=True,
    )


@pytest.fixture
def test_space(test_user):
    """Create a test space."""
    return Space.create(
        organization_id=uuid4(),
        name="Test Space",
        key="TEST",
    )


@pytest.fixture
def test_page(test_space, test_user):
    """Create a test page."""
    return Page.create(
        space_id=test_space.id,
        title="Test Page",
        content="<p>Test content</p>",
        created_by=test_user.id,
    )


class TestExportPageUseCase:
    """Tests for ExportPageUseCase."""

    @pytest.mark.asyncio
    async def test_export_page_to_html_success(self, mock_page_repository, test_page):
        """Test successful page export to HTML."""
        from src.application.use_cases.export import ExportPageUseCase

        mock_page_repository.get_by_id.return_value = test_page

        use_case = ExportPageUseCase(mock_page_repository)
        content, mime_type, filename = await use_case.execute(str(test_page.id), "html")

        assert mime_type == "text/html"
        assert filename == f"{test_page.slug}.html"
        assert b"<!DOCTYPE html>" in content
        assert test_page.title.encode("utf-8") in content

    @pytest.mark.asyncio
    async def test_export_page_to_markdown_success(self, mock_page_repository, test_page):
        """Test successful page export to Markdown."""
        from src.application.use_cases.export import ExportPageUseCase

        mock_page_repository.get_by_id.return_value = test_page

        use_case = ExportPageUseCase(mock_page_repository)
        content, mime_type, filename = await use_case.execute(str(test_page.id), "markdown")

        assert mime_type == "text/markdown"
        assert filename == f"{test_page.slug}.md"
        assert b"# " in content
        assert test_page.title.encode("utf-8") in content

    @pytest.mark.asyncio
    async def test_export_page_to_pdf_success(self, mock_page_repository, test_page):
        """Test successful page export to PDF."""
        from src.application.use_cases.export import ExportPageUseCase

        mock_page_repository.get_by_id.return_value = test_page

        use_case = ExportPageUseCase(mock_page_repository)

        # Mock the _export_to_pdf method directly to avoid weasyprint dependency
        async def mock_export_to_pdf(page):
            return b"%PDF-1.4 fake pdf content", "application/pdf", f"{page.slug}.pdf"

        use_case._export_to_pdf = mock_export_to_pdf

        content, mime_type, filename = await use_case.execute(str(test_page.id), "pdf")

        assert mime_type == "application/pdf"
        assert filename == f"{test_page.slug}.pdf"
        assert len(content) > 0  # PDF should have content

    @pytest.mark.asyncio
    async def test_export_page_invalid_format(self, mock_page_repository, test_page):
        """Test export with invalid format."""
        from src.application.use_cases.export import ExportPageUseCase

        mock_page_repository.get_by_id.return_value = test_page

        use_case = ExportPageUseCase(mock_page_repository)

        with pytest.raises(ValueError, match="Invalid export format"):
            await use_case.execute(str(test_page.id), "invalid")

    @pytest.mark.asyncio
    async def test_export_page_not_found(self, mock_page_repository):
        """Test export when page not found."""
        from src.application.use_cases.export import ExportPageUseCase

        mock_page_repository.get_by_id.return_value = None

        use_case = ExportPageUseCase(mock_page_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()), "html")


class TestExportSpaceUseCase:
    """Tests for ExportSpaceUseCase."""

    @pytest.mark.asyncio
    async def test_export_space_to_html_success(
        self, mock_space_repository, mock_page_repository, test_space, test_page
    ):
        from src.application.use_cases.export import ExportSpaceUseCase

        """Test successful space export to HTML."""
        mock_space_repository.get_by_id.return_value = test_space
        mock_page_repository.get_tree.return_value = [test_page]

        use_case = ExportSpaceUseCase(mock_space_repository, mock_page_repository)
        content, mime_type, filename = await use_case.execute(str(test_space.id), "html")

        assert mime_type == "text/html"
        assert filename == f"{test_space.key.lower()}_export.html"
        assert b"<!DOCTYPE html>" in content
        assert test_space.name.encode("utf-8") in content

    @pytest.mark.asyncio
    async def test_export_space_to_pdf_success(
        self,
        mock_space_repository,
        mock_page_repository,
        test_space,
        test_page,
    ):
        """Test successful space export to PDF."""
        from src.application.use_cases.export import ExportSpaceUseCase

        mock_space_repository.get_by_id.return_value = test_space
        mock_page_repository.get_tree.return_value = [test_page]

        use_case = ExportSpaceUseCase(mock_space_repository, mock_page_repository)

        # Mock the _export_to_pdf method directly to avoid weasyprint dependency
        async def mock_export_to_pdf(space, pages):
            return (
                b"%PDF-1.4 fake pdf content",
                "application/pdf",
                f"{space.key.lower()}_export.pdf",
            )

        use_case._export_to_pdf = mock_export_to_pdf

        content, mime_type, filename = await use_case.execute(str(test_space.id), "pdf")

        assert mime_type == "application/pdf"
        assert filename == f"{test_space.key.lower()}_export.pdf"
        assert len(content) > 0  # PDF should have content

    @pytest.mark.asyncio
    async def test_export_space_not_found(self, mock_space_repository, mock_page_repository):
        """Test export when space not found."""
        from src.application.use_cases.export import ExportSpaceUseCase

        mock_space_repository.get_by_id.return_value = None

        use_case = ExportSpaceUseCase(mock_space_repository, mock_page_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()), "html")
