from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class DomainCreate(BaseModel):
    domain: str


class DomainRead(BaseModel):
    id: uuid.UUID
    site_id: uuid.UUID
    domain: str
    ssl_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DomainUpdate(BaseModel):
    ssl_status: str
