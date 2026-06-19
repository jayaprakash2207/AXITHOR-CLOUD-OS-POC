from __future__ import annotations

import uuid

import structlog
from sqlalchemy.orm import Session

from app.models.file_metadata import FileMetadata
from app.models.site import Site
from app.models.website_file import WebsiteFile
from app.repositories.file_metadata_repository import FileMetadataRepository
from app.schemas.metadata import FileMetadataSyncResult
from app.services.file_validation_service import get_mime_type
from app.services.google_drive_service import GoogleDriveService

logger = structlog.get_logger()


class MetadataService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self._repo = FileMetadataRepository(db)

    def get_latest_for_site(self, site_id: uuid.UUID) -> list[FileMetadata]:
        return self._repo.get_latest_for_site(site_id)

    def get_all_for_site(self, site_id: uuid.UUID) -> list[FileMetadata]:
        return self._repo.get_all_for_site(site_id)

    def get_history(self, site_id: uuid.UUID, path: str) -> list[FileMetadata]:
        return self._repo.get_history(site_id, path)

    def search(self, site_id: uuid.UUID, path_prefix: str) -> list[FileMetadata]:
        return self._repo.search(site_id, path_prefix)

    def validate_checksum(self, site_id: uuid.UUID, path: str, checksum: str) -> bool:
        return self._repo.validate_checksum(site_id, path, checksum)

    async def sync_from_drive(
        self, site: Site, access_token: str
    ) -> FileMetadataSyncResult:
        """Re-sync metadata by querying Drive for current files."""
        drive = GoogleDriveService(access_token)
        drive_files = await drive.list_site_files(site.drive_folder_id)

        added = 0
        updated = 0
        errors: list[str] = []

        for df in drive_files:
            path = df.get("name", "").replace("_", "/", 1)
            file_id = df.get("id", "")
            try:
                existing = self._repo.get_latest(site.id, path)
                record = self._repo.upsert(
                    site_id=site.id,
                    path=path,
                    provider_file_id=file_id,
                )
                if existing is None:
                    added += 1
                elif record.version > existing.version:
                    updated += 1
            except Exception as exc:
                errors.append(f"{path}: {exc}")
                logger.warning("metadata_sync_error", path=path, error=str(exc))

        self.db.commit()
        return FileMetadataSyncResult(
            synced=len(drive_files),
            added=added,
            updated=updated,
            errors=errors,
        )
