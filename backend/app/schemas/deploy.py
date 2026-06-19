from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class DeployedFileRead(BaseModel):
    id: uuid.UUID
    path: str
    provider_file_id: str
    mime_type: str | None
    file_size: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DeploymentResultRead(BaseModel):
    site_id: uuid.UUID
    status: str
    files_deployed: int
    files: list[DeployedFileRead]
    deployment_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class DeploymentRead(BaseModel):
    id: uuid.UUID
    site_id: uuid.UUID
    status: str
    error_message: str | None
    created_at: datetime
    finished_at: datetime | None

    model_config = {"from_attributes": True}
