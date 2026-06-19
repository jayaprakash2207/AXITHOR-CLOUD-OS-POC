"""Comprehensive MIME type registry for static asset serving."""
from __future__ import annotations

_MIME_MAP: dict[str, str] = {
    # Web documents
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".mjs": "application/javascript; charset=utf-8",
    ".cjs": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".xml": "application/xml; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".md": "text/markdown; charset=utf-8",
    ".map": "application/json; charset=utf-8",
    # Images
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".avif": "image/avif",
    # Fonts
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".eot": "application/vnd.ms-fontobject",
    ".otf": "font/otf",
    # Media
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".ogg": "audio/ogg",
    ".mp3": "audio/mpeg",
    # Documents
    ".pdf": "application/pdf",
}

# Extensions that browsers cache aggressively (content-hashed filenames)
_IMMUTABLE_EXTENSIONS = {".woff", ".woff2", ".ttf", ".eot", ".otf", ".png", ".jpg",
                          ".jpeg", ".gif", ".webp", ".avif", ".ico", ".mp4", ".webm",
                          ".ogg", ".mp3", ".pdf"}


def get_mime_type(path: str) -> str:
    """Return the correct Content-Type for a given file path."""
    if "." not in path:
        return "application/octet-stream"
    suffix = "." + path.rsplit(".", 1)[-1].lower()
    return _MIME_MAP.get(suffix, "application/octet-stream")


def is_immutable(path: str) -> bool:
    """True for binary assets that should be cached for 1 year."""
    if "." not in path:
        return False
    suffix = "." + path.rsplit(".", 1)[-1].lower()
    return suffix in _IMMUTABLE_EXTENSIONS


def is_text_type(mime_type: str) -> bool:
    """True for text-based MIME types (used for charset sniffing)."""
    return mime_type.startswith("text/") or mime_type.startswith("application/javascript") or mime_type in (
        "application/json; charset=utf-8",
        "application/xml; charset=utf-8",
        "image/svg+xml",
    )
