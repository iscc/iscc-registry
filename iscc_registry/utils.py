from django.conf import settings
from django.utils.safestring import mark_safe
import mistune
import bleach


def linkify(url: str) -> str:
    """Create clickable link from URL with IPFS support"""
    link = settings.IPFS_GATEWAY + url.replace("ipfs://", "") if url.startswith("ipfs://") else url
    html = f'<a href="{link}" target="top">{url}</a>'
    return mark_safe(html)


def render_markdown(text: str) -> str:
    """Render markdown to secure html"""
    html = mistune.html(text)
    clean = bleach.clean(html, tags=ALLOWED_TAGS, protocols=ALLOWED_PROTOCOLS)
    return mark_safe(clean)


ALLOWED_TAGS = [
    "ul",
    "ol",
    "li",
    "p",
    "pre",
    "code",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "br",
    "strong",
    "em",
    "a",
    "img",
]

ALLOWED_PROTOCOLS = ["http", "https", "mailto", "ipfs"]
