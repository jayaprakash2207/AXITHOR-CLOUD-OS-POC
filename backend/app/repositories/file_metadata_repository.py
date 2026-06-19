from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.file_metadata import FileMetadata
from app.repositories.base import BaseRepository


class FileMetadataRepository(BaseRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def upsert(
        self,
        site_id: uuid.UUID,
        path: str,
        provider_file_id: str,
        checksum: str | None = None,
        provider: str = "google_drive",
    ) -> FileMetadata:
        existing = self.get_latest(site_id, path)
        if existing and existing.checksum == checksum:
            return existing

        new_version = (existing.version + 1) if existing else 1
        record = FileMetadata(
            site_id=site_id,
            path=path,
            provider=provider,
            provider_file_id=provider_file_id,
            checksum=checksum,
            version=new_version,
        )
        self.db.add(record)
        self.db.flush()
        return record

    def get_latest(self, site_id: uuid.UUID, path: str) -> FileMetadata | None:
        return (
            self.db.query(FileMetadata)
            .filter(FileMetadata.site_id == site_id, FileMetadata.path == path)
            .order_by(FileMetadata.version.desc())
            .first()
        )

    def get_latest_for_site(self, site_id: uuid.UUID) -> list[FileMetadata]:
        subq = (
            self.db.query(
                FileMetadata.path,
                FileMetadata.version.label("max_version"),
            )
            .filter(FileMetadata.site_id == site_id)
            .group_by(FileMetadata.path, FileMetadata.version)
            .subquery()
        )
        return (
            self.db.query(FileMetadata)
            .filter(
                FileMetadata.site_id == site_id,
                FileMetadata.path == subq.c.path,
                FileMetadata.version == subq.c.max_version,
            )
            .all()
        )

    def get_all_for_site(self, site_id: uuid.UUID) -> list[FileMetadata]:
        return (
            self.db.query(FileMetadata)
            .filter(FileMetadata.site_id == site_id)
            .order_by(FileMetadata.path, FileMetadata.version)
            .all()
        )

    def get_history(self, site_id: uuid.UUID, path: str) -> list[FileMetadata]:
        return (
            self.db.query(FileMetadata)
            .filter(FileMetadata.site_id == site_id, FileMetadata.path == path)
            .order_by(FileMetadata.version.desc())
            .all()
        )

    def search(self, site_id: uuid.UUID, path_prefix: str) -> list[FileMetadata]:
        return (
            self.db.query(FileMetadata)
            .filter(
                FileMetadata.site_id == site_id,
                FileMetadata.path.like(f"{path_prefix}%"),
            )
            .order_by(FileMetadata.path, FileMetadata.version.desc())
            .all()
        )

    def validate_checksum(self, site_id: uuid.UUID, path: str, checksum: str) -> bool:
        record = self.get_latest(site_id, path)
        if record is None:
            return False
        return record.checksum == checksum
