"""Module 4.5 — Static Asset Resolution Engine."""
from __future__ import annotations

import posixpath
from collections.abc import AsyncIterator

import httpx
import structlog

from app.models.website_file import WebsiteFile
from app.utils.mime_types import get_mime_type, is_immutable

logger = structlog.get_logger()

_DRIVE_FILES_URL = "https://www.googleapis.com/drive/v3/files"
_CHUNK_SIZE = 64 * 1024  # 64 KB streaming chunks

_ERROR_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>{code} {title}</title>
<style>
  body{{margin:0;background:#0d1f1a;color:#fff;font-family:sans-serif;
        display:flex;align-items:center;justify-content:center;height:100vh;flex-direction:column}}
  h1{{font-size:4rem;color:#4ade80;margin:0}} p{{color:#ffffff80}}
  a{{color:#4ade80;text-decoration:none}}
</style></head>
<body><h1>{code}</h1><p>{message}</p><p><a href="/">← home</a></p></body>
</html>"""


class AssetNotFoundError(Exception):
    pass


class AssetResolutionError(Exception):
    pass


# ---------------------------------------------------------------------------
# Path security
# ---------------------------------------------------------------------------

def sanitize_path(raw: str) -> str | None:
    """
    Normalize a URL path and reject any traversal attempts.

    Returns the clean relative path (e.g. "css/style.css") or None if unsafe.
    """
    if not raw:
        return "index.html"

    # Null-byte injection
    if "\x00" in raw:
        return None

    # Windows-style separator smuggling
    if "\\" in raw:
        return None

    # Percent-encoded traversal sequences (decoded forms caught by normpath below,
    # but reject the encoded forms explicitly)
    lower = raw.lower()
    if "%2e%2e" in lower or "%2f" in lower or "%5c" in lower:
        return None

    # Reject literal .. segments before normpath collapses them away
    if ".." in raw.split("/"):
        return None

    # Normalize using POSIX semantics: collapses .., ., double slashes
    normalized = posixpath.normpath("/" + raw.lstrip("/"))

    # After normpath the path always starts with /; strip it
    clean = normalized.lstrip("/")

    # Paranoia check: normpath should have removed all ..
    if ".." in clean.split("/"):
        return None

    return clean or "index.html"


# ---------------------------------------------------------------------------
# Cache headers
# ---------------------------------------------------------------------------

def build_cache_headers(file: WebsiteFile, mime_type: str) -> dict[str, str]:
    """Return ETag, Cache-Control, Last-Modified, and Vary headers."""
    etag = f'"{file.provider_file_id}"'

    headers: dict[str, str] = {
        "ETag": etag,
        "Vary": "Accept-Encoding",
        "X-Served-By": "Axithor-Edge",
    }

    if file.created_at:
        headers["Last-Modified"] = file.created_at.strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Long cache for hashed/immutable assets; revalidate for HTML
    if is_immutable(file.path):
        headers["Cache-Control"] = "public, max-age=31536000, immutable"
    elif "text/html" in mime_type:
        headers["Cache-Control"] = "public, no-cache"
    else:
        headers["Cache-Control"] = "public, max-age=3600"

    return headers


def check_not_modified(file: WebsiteFile, if_none_match: str | None) -> bool:
    """
    Return True when the client's cached copy is still fresh (ETag match).
    Handles both strong and weak ETags, and the wildcard '*'.
    """
    if not if_none_match:
        return False
    server_tag = file.provider_file_id
    for token in if_none_match.split(","):
        token = token.strip().strip('"').lstrip("W/").strip('"')
        if token == "*" or token == server_tag:
            return True
    return False


# ---------------------------------------------------------------------------
# Streaming
# ---------------------------------------------------------------------------

async def stream_drive_file(file_id: str, access_token: str) -> AsyncIterator[bytes]:
    """
    Stream a Google Drive file to the caller in 64 KB chunks.

    Raises AssetNotFoundError if Drive returns 404.
    Raises AssetResolutionError on other HTTP errors.
    """
    url = f"{_DRIVE_FILES_URL}/{file_id}"
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    timeout = httpx.Timeout(connect=10.0, read=120.0, write=10.0, pool=5.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream("GET", url, params={"alt": "media"}, headers=auth_headers) as resp:
            if resp.status_code == 404:
                raise AssetNotFoundError(f"Drive file not found: {file_id}")
            if resp.status_code == 401:
                raise AssetResolutionError("Drive access token expired or revoked")
            if not resp.is_success:
                raise AssetResolutionError(f"Drive returned HTTP {resp.status_code}")
            async for chunk in resp.aiter_bytes(_CHUNK_SIZE):
                yield chunk


# ---------------------------------------------------------------------------
# HTML error responses
# ---------------------------------------------------------------------------

def make_error_html(code: int, title: str, message: str) -> str:
    return _ERROR_HTML.format(code=code, title=title, message=message)
