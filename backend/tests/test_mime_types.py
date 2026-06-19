"""Tests for app.utils.mime_types."""
from __future__ import annotations

import pytest

from app.utils.mime_types import get_mime_type, is_immutable, is_text_type


class TestGetMimeType:
    def test_html(self):
        assert get_mime_type("index.html") == "text/html; charset=utf-8"

    def test_htm(self):
        assert get_mime_type("page.htm") == "text/html; charset=utf-8"

    def test_css(self):
        assert get_mime_type("style.css") == "text/css; charset=utf-8"

    def test_js(self):
        assert get_mime_type("app.js") == "application/javascript; charset=utf-8"

    def test_mjs(self):
        assert get_mime_type("module.mjs") == "application/javascript; charset=utf-8"

    def test_json(self):
        assert get_mime_type("data.json") == "application/json; charset=utf-8"

    def test_svg(self):
        assert get_mime_type("icon.svg") == "image/svg+xml"

    def test_png(self):
        assert get_mime_type("logo.png") == "image/png"

    def test_jpg(self):
        assert get_mime_type("photo.jpg") == "image/jpeg"

    def test_jpeg(self):
        assert get_mime_type("photo.jpeg") == "image/jpeg"

    def test_webp(self):
        assert get_mime_type("image.webp") == "image/webp"

    def test_gif(self):
        assert get_mime_type("anim.gif") == "image/gif"

    def test_ico(self):
        assert get_mime_type("favicon.ico") == "image/x-icon"

    def test_avif(self):
        assert get_mime_type("hero.avif") == "image/avif"

    def test_woff(self):
        assert get_mime_type("font.woff") == "font/woff"

    def test_woff2(self):
        assert get_mime_type("font.woff2") == "font/woff2"

    def test_ttf(self):
        assert get_mime_type("font.ttf") == "font/ttf"

    def test_txt(self):
        assert get_mime_type("readme.txt") == "text/plain; charset=utf-8"

    def test_source_map(self):
        assert get_mime_type("app.js.map") == "application/json; charset=utf-8"

    def test_unknown_extension_fallback(self):
        assert get_mime_type("file.xyz") == "application/octet-stream"

    def test_no_extension_fallback(self):
        assert get_mime_type("CNAME") == "application/octet-stream"

    def test_uppercase_extension(self):
        # Extension comparison is case-insensitive
        assert get_mime_type("IMAGE.PNG") == "image/png"

    def test_nested_path(self):
        assert get_mime_type("assets/images/logo.png") == "image/png"

    def test_dotfile(self):
        assert get_mime_type(".htaccess") == "application/octet-stream"


class TestIsImmutable:
    def test_font_is_immutable(self):
        assert is_immutable("fonts/roboto.woff2") is True

    def test_image_is_immutable(self):
        assert is_immutable("images/logo.png") is True

    def test_html_not_immutable(self):
        assert is_immutable("index.html") is False

    def test_css_not_immutable(self):
        assert is_immutable("style.css") is False

    def test_js_not_immutable(self):
        assert is_immutable("app.js") is False


class TestIsTextType:
    def test_html_is_text(self):
        assert is_text_type("text/html; charset=utf-8") is True

    def test_css_is_text(self):
        assert is_text_type("text/css; charset=utf-8") is True

    def test_js_is_text(self):
        assert is_text_type("application/javascript; charset=utf-8") is True

    def test_png_not_text(self):
        assert is_text_type("image/png") is False
