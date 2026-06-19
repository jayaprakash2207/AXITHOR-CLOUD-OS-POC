"""Tests for the /serve/{subdomain}/{path} endpoint (Module 4.5)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.website_file import WebsiteFile


def _make_file(path: str, provider_id: str = "drive_abc", mime: str = "text/html; charset=utf-8") -> WebsiteFile:
    f = WebsiteFile()
    f.id = uuid.uuid4()
    f.site_id = uuid.uuid4()
    f.path = path
    f.provider_file_id = provider_id
    f.mime_type = mime
    f.file_size = 100
    f.created_at = datetime(2026, 6, 19, tzinfo=timezone.utc)
    return f


def _make_site(subdomain: str = "testsite"):
    site = MagicMock()
    site.id = uuid.uuid4()
    site.subdomain = subdomain
    site.status = "deployed"
    return site


client = TestClient(app, raise_server_exceptions=False)


class TestServeEndpoint:
    def test_unknown_subdomain_returns_404_html(self):
        with patch("app.services.subdomain_service.SubdomainService.resolve_site",
                   side_effect=Exception("not found")):
            resp = client.get("/serve/unknownxyz/")
        assert resp.status_code in (404, 503)
        assert "text/html" in resp.headers.get("content-type", "")

    def test_path_traversal_returns_400(self):
        resp = client.get("/serve/testsite/../../../etc/passwd")
        # Either 400 (blocked) or 404 (site not found), never 200
        assert resp.status_code in (400, 404)

    def test_null_byte_path_returns_400_or_404(self):
        resp = client.get("/serve/testsite/index.html%00.php")
        assert resp.status_code in (400, 404)

    def test_correct_mime_type_for_css(self):
        site = _make_site()
        css = _make_file("css/style.css", "drive_css", "text/css; charset=utf-8")

        with (
            patch("app.services.subdomain_service.SubdomainService.resolve_site", return_value=site),
            patch("app.services.subdomain_service.SubdomainService.resolve_file", return_value=css),
            patch("app.api.v1.routes.serve._resolve_access_token", return_value="fake_token"),
            patch("app.api.v1.routes.serve.stream_drive_file", return_value=_fake_stream(b"body { color: red; }")),
        ):
            resp = client.get("/serve/testsite/css/style.css")

        assert resp.status_code == 200
        assert "text/css" in resp.headers["content-type"]

    def test_etag_header_present(self):
        site = _make_site()
        f = _make_file("index.html", "drive_xyz")

        with (
            patch("app.services.subdomain_service.SubdomainService.resolve_site", return_value=site),
            patch("app.services.subdomain_service.SubdomainService.resolve_file", return_value=f),
            patch("app.api.v1.routes.serve._resolve_access_token", return_value="fake_token"),
            patch("app.api.v1.routes.serve.stream_drive_file", return_value=_fake_stream(b"<html></html>")),
        ):
            resp = client.get("/serve/testsite/")

        assert resp.status_code == 200
        assert resp.headers.get("etag") == '"drive_xyz"'

    def test_304_on_matching_etag(self):
        site = _make_site()
        f = _make_file("index.html", "drive_xyz")

        with (
            patch("app.services.subdomain_service.SubdomainService.resolve_site", return_value=site),
            patch("app.services.subdomain_service.SubdomainService.resolve_file", return_value=f),
            patch("app.api.v1.routes.serve._resolve_access_token", return_value="fake_token"),
        ):
            resp = client.get("/serve/testsite/", headers={"if-none-match": '"drive_xyz"'})

        assert resp.status_code == 304

    def test_served_by_header(self):
        site = _make_site()
        f = _make_file("index.html")

        with (
            patch("app.services.subdomain_service.SubdomainService.resolve_site", return_value=site),
            patch("app.services.subdomain_service.SubdomainService.resolve_file", return_value=f),
            patch("app.api.v1.routes.serve._resolve_access_token", return_value="fake_token"),
            patch("app.api.v1.routes.serve.stream_drive_file", return_value=_fake_stream(b"html")),
        ):
            resp = client.get("/serve/testsite/")

        assert resp.headers.get("x-served-by") == "Axithor-Edge"

    def test_no_storage_returns_503_html(self):
        site = _make_site()
        f = _make_file("index.html")

        with (
            patch("app.services.subdomain_service.SubdomainService.resolve_site", return_value=site),
            patch("app.services.subdomain_service.SubdomainService.resolve_file", return_value=f),
            patch("app.api.v1.routes.serve._resolve_access_token", return_value=None),
        ):
            resp = client.get("/serve/testsite/")

        assert resp.status_code == 503
        assert "text/html" in resp.headers["content-type"]

    def test_cache_control_immutable_for_fonts(self):
        site = _make_site()
        font = _make_file("fonts/roboto.woff2", "drive_font", "font/woff2")

        with (
            patch("app.services.subdomain_service.SubdomainService.resolve_site", return_value=site),
            patch("app.services.subdomain_service.SubdomainService.resolve_file", return_value=font),
            patch("app.api.v1.routes.serve._resolve_access_token", return_value="fake_token"),
            patch("app.api.v1.routes.serve.stream_drive_file", return_value=_fake_stream(b"\x00\x01font")),
        ):
            resp = client.get("/serve/testsite/fonts/roboto.woff2")

        assert resp.status_code == 200
        assert "immutable" in resp.headers.get("cache-control", "")

    def test_cache_control_no_cache_for_html(self):
        site = _make_site()
        f = _make_file("index.html")

        with (
            patch("app.services.subdomain_service.SubdomainService.resolve_site", return_value=site),
            patch("app.services.subdomain_service.SubdomainService.resolve_file", return_value=f),
            patch("app.api.v1.routes.serve._resolve_access_token", return_value="fake_token"),
            patch("app.api.v1.routes.serve.stream_drive_file", return_value=_fake_stream(b"<html/>")),
        ):
            resp = client.get("/serve/testsite/")

        cc = resp.headers.get("cache-control", "")
        assert "no-cache" in cc or "must-revalidate" in cc


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _fake_stream(data: bytes):
    """Async generator that yields a single chunk."""
    yield data
