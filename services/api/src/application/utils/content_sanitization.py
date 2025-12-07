"""Content sanitization utilities for XSS prevention."""

from typing import Any

try:
    from bleach import clean, linkify
    from bleach.css_sanitizer import CSSSanitizer
except ImportError:
    # Fallback if bleach is not installed
    clean: Any = None  # type: ignore[assignment,no-redef]
    linkify: Any = None  # type: ignore[assignment,no-redef]
    CSSSanitizer: Any = None  # type: ignore[assignment,no-redef]

# Allowed HTML tags for rich text content
ALLOWED_TAGS = [
    "p",
    "br",
    "strong",
    "em",
    "u",
    "s",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "blockquote",
    "code",
    "pre",
    "a",
    "img",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "hr",
    "div",
    "span",
]

# Allowed HTML attributes
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "code": ["class"],
    "pre": ["class"],
    "div": ["class"],
    "span": ["class"],
    "table": ["class"],
    "th": ["class", "colspan", "rowspan"],
    "td": ["class", "colspan", "rowspan"],
}

# Allowed CSS classes (for syntax highlighting, etc.)
ALLOWED_CSS_CLASSES = [
    "language-python",
    "language-javascript",
    "language-json",
    "language-html",
    "language-css",
    "language-sql",
    "hljs",
    "code-block",
]


def sanitize_html(html_content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks.

    Args:
        html_content: Raw HTML content

    Returns:
        Sanitized HTML content

    Raises:
        ImportError: If bleach is not installed
    """
    if clean is None:
        raise ImportError(
            "bleach is required for content sanitization. Install it with: pip install bleach"
        )

    # Create CSS sanitizer
    css_sanitizer = CSSSanitizer(allowed_css_properties=["color", "background-color"])

    # Sanitize HTML
    sanitized: str = clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        css_sanitizer=css_sanitizer,
        strip=True,  # Strip disallowed tags instead of escaping
    )

    # Auto-linkify URLs
    if linkify is not None:
        sanitized = linkify(sanitized, parse_email=False)

    return sanitized


def sanitize_markdown(markdown_content: str) -> str:
    """Sanitize markdown content (basic validation).

    Args:
        markdown_content: Raw markdown content

    Returns:
        Sanitized markdown content (same as input for now, can add validation)
    """
    # For markdown, we'll sanitize after conversion to HTML
    # This function can be used for basic validation if needed
    return markdown_content.strip()
