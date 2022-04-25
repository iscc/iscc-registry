from django.conf import settings
from django.utils.safestring import mark_safe


def linkify(url: str) -> str:
    """Create clickable link from URL with IPFS support"""
    link = settings.IPFS_GATEWAY + url.replace("ipfs://", "") if url.startswith("ipfs://") else url
    html = f'<a href="{link}" target="top">{url}</a>'
    return mark_safe(html)
