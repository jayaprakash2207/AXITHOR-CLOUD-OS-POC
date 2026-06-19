from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class FileMetadataRead(BaseModel):
    id: uuid.UUID
    site_id: uuid.UUID
    path: str
    provider: str
    provider_file_id: str
    checksum: str | None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FileMetadataSearch(BaseModel):
    site_id: uuid.UUID
    path: str | None = None
    provider: str | None = None
    version: int | None = None


class FileMetadataSyncResult(BaseModel):
    synced: int
    added: int
    updated: int
    errors: list[str]
