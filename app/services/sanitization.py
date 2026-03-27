"""HTML sanitization for rich text fields (Trix editor output)."""

import nh3

_ALLOWED_TAGS = {"p", "br", "strong", "em", "a", "ul", "ol", "li",
                 "blockquote", "h1", "h2", "h3", "pre", "code", "del",
                 "figure", "figcaption", "div"}
_ALLOWED_ATTRIBUTES = {"a": {"href", "title"}}

# Fields that accept rich text and must be sanitized on write
RICH_TEXT_FIELDS = {"bio", "obituary", "research_notes"}


def sanitize_html(value: str | None) -> str:
    """Sanitize HTML, allowing only safe tags from Trix editor."""
    if not value:
        return value or ""
    return nh3.clean(value, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRIBUTES)
