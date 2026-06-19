from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.website_file import WebsiteFile
from app.repositories.base import BaseRepository


class WebsiteFileRepository(BaseRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def create(
        self,
        site_id: uuid.UUID,
        path: str,
        provider_file_id: str,
        mime_type: str | None = None,
        file_size: int | None = None,
    ) -> WebsiteFile:
        record = WebsiteFile(
            site_id=site_id,
            path=path,
            provider_file_id=provider_file_id,
            mime_type=mime_type,
            file_size=file_size,
        )
        self.db.add(record)
        self.db.flush()
        return record

    def get_by_site(self, site_id: uuid.UUID) -> list[WebsiteFile]:
        return (
            self.db.query(WebsiteFile)
            .filter(WebsiteFile.site_id == site_id)
            .order_by(WebsiteFile.path)
            .all()
        )

    def get_by_path(self, site_id: uuid.UUID, path: str) -> WebsiteFile | None:
        return (
            self.db.query(WebsiteFile)
            .filter(WebsiteFile.site_id == site_id, WebsiteFile.path == path)
            .first()
        )

    def delete_by_site(self, site_id: uuid.UUID) -> int:
        count = (
            self.db.query(WebsiteFile).filter(WebsiteFile.site_id == site_id).delete()
        )
        self.db.flush()
        return count
