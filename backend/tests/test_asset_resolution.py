"""Tests for app.services.asset_resolution_service."""
from __future__ import annotations

import pytest

from app.services.asset_resolution_service import (
    build_cache_headers,
    check_not_modified,
    sanitize_path,
)


# ---------------------------------------------------------------------------
# sanitize_path — security tests
# ---------------------------------------------------------------------------

class TestSanitizePath:
    # --- Valid paths ---
    def test_empty_returns_index(self):
        assert sanitize_path("") == "index.html"

    def test_bare_filename(self):
        assert sanitize_path("index.html") == "index.html"

    def test_nested_path(self):
        assert sanitize_path("css/style.css") == "css/style.css"

    def test_deeply_nested(self):
        assert sanitize_path("assets/images/hero.png") == "assets/images/hero.png"

    def test_leading_slash_stripped(self):
        assert sanitize_path("/css/style.css") == "css/style.css"

    def test_double_slash_collapsed(self):
        assert sanitize_path("css//style.css") == "css/style.css"

    def test_dot_segment_collapsed(self):
        assert sanitize_path("css/./style.css") == "css/style.css"

    # --- Traversal attacks ---
    def test_dotdot_rejected(self):
        assert sanitize_path("../etc/passwd") is None

    def test_dotdot_in_middle_rejected(self):
        assert sanitize_path("css/../../../etc/passwd") is None

    def test_encoded_dotdot_rejected(self):
        assert sanitize_path("%2e%2e/etc/passwd") is None

    def test_encoded_slash_rejected(self):
        assert sanitize_path("css%2fstyle.css") is None

    def test_windows_separator_rejected(self):
        assert sanitize_path("css\\style.css") is None

    def test_null_byte_rejected(self):
        assert sanitize_path("index.html\x00.php") is None

    def test_encoded_backslash_rejected(self):
        assert sanitize_path("css%5cstyle.css") is None

    def test_absolute_path_traversal(self):
        # Attempts to reach /etc/passwd via absolute path in URL
        assert sanitize_path("////etc/passwd") == "etc/passwd"  # collapses safely

    def test_percent_encoded_dotdot_upper(self):
        assert sanitize_path("%2E%2E/secret") is None


# ---------------------------------------------------------------------------
# build_cache_headers
# ---------------------------------------------------------------------------

class TestBuildCacheHeaders:
    def test_html_gets_no_cache(self, sample_file):
        sample_file.path = "index.html"
        headers = build_cache_headers(sample_file, "text/html; charset=utf-8")
        assert "no-cache" in headers["Cache-Control"]

    def test_font_gets_immutable(self, font_file):
        headers = build_cache_headers(font_file, "font/woff2")
        assert "immutable" in headers["Cache-Control"]
        assert "31536000" in headers["Cache-Control"]

    def test_image_gets_immutable(self, sample_file):
        sample_file.path = "logo.png"
        headers = build_cache_headers(sample_file, "image/png")
        assert "immutable" in headers["Cache-Control"]

    def test_css_gets_1h_cache(self, css_file):
        headers = build_cache_headers(css_file, "text/css; charset=utf-8")
        assert "3600" in headers["Cache-Control"]

    def test_etag_set(self, sample_file):
        headers = build_cache_headers(sample_file, "text/html; charset=utf-8")
        assert headers["ETag"] == f'"{sample_file.provider_file_id}"'

    def test_last_modified_set(self, sample_file):
        headers = build_cache_headers(sample_file, "text/html; charset=utf-8")
        assert "Last-Modified" in headers
        assert "2026" in headers["Last-Modified"]

    def test_served_by_header(self, sample_file):
        headers = build_cache_headers(sample_file, "text/html; charset=utf-8")
        assert headers["X-Served-By"] == "Axithor-Edge"

    def test_vary_header(self, sample_file):
        headers = build_cache_headers(sample_file, "text/html; charset=utf-8")
        assert headers["Vary"] == "Accept-Encoding"


# ---------------------------------------------------------------------------
# check_not_modified — ETag validation
# ---------------------------------------------------------------------------

class TestCheckNotModified:
    def test_matching_etag_returns_true(self, sample_file):
        etag_header = f'"{sample_file.provider_file_id}"'
        assert check_not_modified(sample_file, etag_header) is True

    def test_wildcard_returns_true(self, sample_file):
        assert check_not_modified(sample_file, "*") is True

    def test_mismatched_etag_returns_false(self, sample_file):
        assert check_not_modified(sample_file, '"other_file_id"') is False

    def test_no_header_returns_false(self, sample_file):
        assert check_not_modified(sample_file, None) is False

    def test_multiple_etags_one_matches(self, sample_file):
        etag_header = f'"old_id", "{sample_file.provider_file_id}"'
        assert check_not_modified(sample_file, etag_header) is True

    def test_weak_etag_matches(self, sample_file):
        etag_header = f'W/"{sample_file.provider_file_id}"'
        assert check_not_modified(sample_file, etag_header) is True
