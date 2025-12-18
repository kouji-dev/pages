"""Export page use case."""

from uuid import UUID

import structlog

from src.domain.entities import Page
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageRepository

logger = structlog.get_logger()

# Export format constants
EXPORT_FORMAT_PDF = "pdf"
EXPORT_FORMAT_MARKDOWN = "markdown"
EXPORT_FORMAT_HTML = "html"


class ExportPageUseCase:
    """Use case for exporting a page to various formats."""

    def __init__(self, page_repository: PageRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            page_repository: Page repository
        """
        self._page_repository = page_repository

    async def execute(
        self,
        page_id: str,
        export_format: str,
    ) -> tuple[bytes, str, str]:
        """Execute export page.

        Args:
            page_id: Page ID
            export_format: Export format (pdf, markdown, html)

        Returns:
            Tuple of (file_content, mime_type, filename)

        Raises:
            EntityNotFoundException: If page not found
            ValueError: If export format is invalid
        """
        logger.info("Exporting page", page_id=page_id, format=export_format)

        page_uuid = UUID(page_id)
        page = await self._page_repository.get_by_id(page_uuid)

        if page is None:
            logger.warning("Page not found for export", page_id=page_id)
            raise EntityNotFoundException("Page", page_id)

        # Validate export format
        valid_formats = {EXPORT_FORMAT_PDF, EXPORT_FORMAT_MARKDOWN, EXPORT_FORMAT_HTML}
        if export_format.lower() not in valid_formats:
            raise ValueError(f"Invalid export format. Must be one of: {', '.join(valid_formats)}")

        format_lower = export_format.lower()

        # Export based on format
        if format_lower == EXPORT_FORMAT_PDF:
            return await self._export_to_pdf(page)
        elif format_lower == EXPORT_FORMAT_MARKDOWN:
            return await self._export_to_markdown(page)
        elif format_lower == EXPORT_FORMAT_HTML:
            return await self._export_to_html(page)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")

    async def _export_to_pdf(self, page: Page) -> tuple[bytes, str, str]:
        """Export page to PDF.

        Args:
            page: Page entity

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

        # Convert content to HTML if needed
        html_content = page.content or ""
        if not html_content.strip():
            html_content = f"<h1>{page.title}</h1>"

        # Create full HTML document
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{page.title}</title>
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
            </style>
        </head>
        <body>
            <h1>{page.title}</h1>
            {html_content}
        </body>
        </html>
        """

        # Generate PDF
        font_config = FontConfiguration()
        pdf_bytes = HTML(string=full_html).write_pdf(font_config=font_config)

        filename = f"{page.slug}.pdf"
        return pdf_bytes, "application/pdf", filename

    async def _export_to_markdown(self, page: Page) -> tuple[bytes, str, str]:
        """Export page to Markdown.

        Args:
            page: Page entity

        Returns:
            Tuple of (Markdown bytes, mime_type, filename)
        """
        try:
            import html2text
        except ImportError as err:
            raise ImportError(
                "html2text is required for Markdown export. Install it with: pip install html2text"
            ) from err

        # Convert HTML to Markdown
        html_content = page.content or ""
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        markdown_content = h.handle(html_content)

        # Add title as header
        full_markdown = f"# {page.title}\n\n{markdown_content}"

        filename = f"{page.slug}.md"
        return full_markdown.encode("utf-8"), "text/markdown", filename

    async def _export_to_html(self, page: Page) -> tuple[bytes, str, str]:
        """Export page to HTML.

        Args:
            page: Page entity

        Returns:
            Tuple of (HTML bytes, mime_type, filename)
        """
        html_content = page.content or ""

        # Create full HTML document
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{page.title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }}
    </style>
</head>
<body>
    <h1>{page.title}</h1>
    {html_content}
</body>
</html>"""

        filename = f"{page.slug}.html"
        return full_html.encode("utf-8"), "text/html", filename
