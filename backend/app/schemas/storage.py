from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class StorageAccountRead(BaseModel):
    id: UUID
    user_id: UUID
    provider: str
    quota: str | None
    created_at: datetime


class StorageUsageRead(BaseModel):
    storage_quota: dict[str, int | str | None]
    drive_metadata: dict[str, str | int | None]
