"""Export space use case."""

from uuid import UUID

import structlog

from src.domain.entities import Page, Space
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageRepository, SpaceRepository

logger = structlog.get_logger()


class ExportSpaceUseCase:
    """Use case for exporting a space (all pages) to various formats."""

    def __init__(
        self,
        space_repository: SpaceRepository,
        page_repository: PageRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            space_repository: Space repository
            page_repository: Page repository
        """
        self._space_repository = space_repository
        self._page_repository = page_repository

    async def execute(
        self,
        space_id: str,
        export_format: str = "html",
    ) -> tuple[bytes, str, str]:
        """Execute export space.

        Args:
            space_id: Space ID
            export_format: Export format (html, markdown, pdf)

        Returns:
            Tuple of (file_content, mime_type, filename)

        Raises:
            EntityNotFoundException: If space not found
            ValueError: If export format is invalid
        """
        logger.info("Exporting space", space_id=space_id, format=export_format)

        space_uuid = UUID(space_id)
        space = await self._space_repository.get_by_id(space_uuid)

        if space is None:
            logger.warning("Space not found for export", space_id=space_id)
            raise EntityNotFoundException("Space", space_id)

        # Get all pages in space
        pages = await self._page_repository.get_tree(space_uuid)

        # Validate export format
        valid_formats = {"html", "markdown", "pdf"}
        if export_format.lower() not in valid_formats:
            raise ValueError(f"Invalid export format. Must be one of: {', '.join(valid_formats)}")

        format_lower = export_format.lower()

        # Export based on format
        if format_lower == "html":
            return await self._export_to_html(space, pages)
        elif format_lower == "markdown":
            return await self._export_to_markdown(space, pages)
        elif format_lower == "pdf":
            return await self._export_to_pdf(space, pages)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")

    async def _export_to_html(self, space: Space, pages: list[Page]) -> tuple[bytes, str, str]:
        """Export space to HTML.

        Args:
            space: Space entity
            pages: List of pages in space

        Returns:
            Tuple of (HTML bytes, mime_type, filename)
        """
        html_parts = [
            f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{space.name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }}
        .page {{
            margin-bottom: 40px;
            page-break-after: always;
        }}
        .page-title {{
            font-size: 24px;
            color: #333;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <h1>{space.name}</h1>""",
        ]

        for page in pages:
            html_parts.append(
                f"""
    <div class="page">
        <div class="page-title">{page.title}</div>
        <div class="page-content">{page.content or ''}</div>
    </div>"""
            )

        html_parts.append("</body></html>")
        full_html = "\n".join(html_parts)

        filename = f"{space.key.lower()}_export.html"
        return full_html.encode("utf-8"), "text/html", filename

    async def _export_to_markdown(self, space: Space, pages: list[Page]) -> tuple[bytes, str, str]:
        """Export space to Markdown.

        Args:
            space: Space entity
            pages: List of pages in space

        Returns:
            Tuple of (Markdown bytes, mime_type, filename)
        """
        try:
            import html2text
        except ImportError as err:
            raise ImportError(
                "html2text is required for Markdown export. Install it with: pip install html2text"
            ) from err

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False

        markdown_parts = [f"# {space.name}\n\n"]

        for page in pages:
            page_content = page.content or ""
            markdown_content = h.handle(page_content)
            markdown_parts.append(f"## {page.title}\n\n{markdown_content}\n\n")

        full_markdown = "\n".join(markdown_parts)
        filename = f"{space.key.lower()}_export.md"
        return full_markdown.encode("utf-8"), "text/markdown", filename

    async def _export_to_pdf(self, space: Space, pages: list[Page]) -> tuple[bytes, str, str]:
        """Export space to PDF.

        Args:
            space: Space entity
            pages: List of pages in space

        Returns:
            Tuple of (PDF bytes, mime_type, filename)
        """
        try:
            from weasyprint import HTML  # type: ignore[import-untyped]
            from weasyprint.text.fonts import FontConfiguration  # type: ignore[import-untyped]
        except ImportError as err:
            raise ImportError(
                "weasyprint is required for PDF export. Install it with: pip install weasyprint"
            ) from err

        html_parts = [
            f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{space.name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }}
        .page {{
            margin-bottom: 40px;
            page-break-after: always;
        }}
        .page-title {{
            font-size: 24px;
            color: #333;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <h1>{space.name}</h1>""",
        ]

        for page in pages:
            html_parts.append(
                f"""
    <div class="page">
        <div class="page-title">{page.title}</div>
        <div class="page-content">{page.content or ''}</div>
    </div>"""
            )

        html_parts.append("</body></html>")
        full_html = "\n".join(html_parts)

        font_config = FontConfiguration()
        pdf_bytes = HTML(string=full_html).write_pdf(font_config=font_config)

        filename = f"{space.key.lower()}_export.pdf"
        return pdf_bytes, "application/pdf", filename
