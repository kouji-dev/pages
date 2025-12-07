"""Markdown to HTML conversion utilities."""

try:
    import markdown
    from markdown.extensions import codehilite, fenced_code, tables, toc
except ImportError:
    # Fallback if markdown is not installed
    markdown = None  # type: ignore[assignment]
    codehilite = None  # type: ignore[assignment]
    fenced_code = None  # type: ignore[assignment]
    tables = None  # type: ignore[assignment]
    toc = None  # type: ignore[assignment]

from src.application.utils.content_sanitization import sanitize_html


def markdown_to_html(markdown_content: str, sanitize: bool = True) -> str:
    """Convert markdown content to HTML.

    Args:
        markdown_content: Markdown content to convert
        sanitize: Whether to sanitize the resulting HTML (default: True)

    Returns:
        HTML content

    Raises:
        ImportError: If markdown library is not installed
    """
    if markdown is None:
        raise ImportError(
            "markdown is required for markdown conversion. Install it with: pip install markdown"
        )

    # Configure markdown extensions
    extensions = [
        "fenced_code",
        "codehilite",
        "tables",
        "toc",
        "nl2br",  # Convert newlines to <br>
    ]

    # Convert markdown to HTML
    html: str = markdown.markdown(
        markdown_content,
        extensions=extensions,
        extension_configs={
            "codehilite": {
                "css_class": "hljs",
                "use_pygments": False,  # Disable pygments for now (optional dependency)
            },
            "toc": {
                "permalink": True,
            },
        },
    )

    # Sanitize HTML to prevent XSS
    if sanitize:
        html = sanitize_html(html)

    return html


def html_to_markdown(html_content: str) -> str:
    """Convert HTML content to markdown (basic conversion).

    Note: This is a simplified conversion. For full HTML to markdown conversion,
    consider using a library like html2text or markdownify.

    Args:
        html_content: HTML content to convert

    Returns:
        Markdown content (simplified)
    """
    # Basic HTML to markdown conversion
    # For MVP, we'll keep content as HTML
    # Full conversion can be added later if needed
    return html_content
