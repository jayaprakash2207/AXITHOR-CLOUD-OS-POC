from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class SyncEventRead(BaseModel):
    id: uuid.UUID
    site_id: uuid.UUID | None
    event_type: str
    provider_resource_id: str | None
    status: str
    retry_count: int
    error: str | None
    created_at: datetime
    processed_at: datetime | None

    model_config = {"from_attributes": True}


class DriveWebhookPayload(BaseModel):
    kind: str = ""
    id: str = ""
    resourceId: str = ""
    resourceUri: str = ""
    token: str = ""
    expiration: str = ""


class WatchChannelCreate(BaseModel):
    site_id: uuid.UUID
    channel_id: str | None = None


class WatchChannelRead(BaseModel):
    channel_id: str
    resource_id: str
    expiration: str
    site_id: uuid.UUID
