from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SiteCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    subdomain: str = Field(min_length=3, max_length=63)
    drive_folder_id: str | None = Field(default=None, max_length=255)
    custom_domain: str | None = Field(default=None, max_length=255)


class SiteRead(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    subdomain: str
    drive_folder_id: str | None
    custom_domain: str | None
    status: str
    created_at: datetime
    updated_at: datetime
