"""Shared pytest fixtures for Module 4.5 tests."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.website_file import WebsiteFile


@pytest.fixture()
def sample_file() -> WebsiteFile:
    f = WebsiteFile()
    f.id = uuid.uuid4()
    f.site_id = uuid.uuid4()
    f.path = "index.html"
    f.provider_file_id = "drive_abc123"
    f.mime_type = "text/html; charset=utf-8"
    f.file_size = 512
    f.created_at = datetime(2026, 6, 19, 12, 0, 0, tzinfo=timezone.utc)
    return f


@pytest.fixture()
def css_file() -> WebsiteFile:
    f = WebsiteFile()
    f.id = uuid.uuid4()
    f.site_id = uuid.uuid4()
    f.path = "css/style.css"
    f.provider_file_id = "drive_css456"
    f.mime_type = "text/css; charset=utf-8"
    f.file_size = 2048
    f.created_at = datetime(2026, 6, 19, 12, 0, 0, tzinfo=timezone.utc)
    return f


@pytest.fixture()
def font_file() -> WebsiteFile:
    f = WebsiteFile()
    f.id = uuid.uuid4()
    f.site_id = uuid.uuid4()
    f.path = "fonts/roboto.woff2"
    f.provider_file_id = "drive_font789"
    f.mime_type = "font/woff2"
    f.file_size = 24000
    f.created_at = datetime(2026, 6, 19, 12, 0, 0, tzinfo=timezone.utc)
    return f
