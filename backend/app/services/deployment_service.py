from __future__ import annotations

import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy.orm import Session

from app.models.deployment import Deployment
from app.models.site import Site
from app.repositories.file_metadata_repository import FileMetadataRepository
from app.repositories.website_file_repository import WebsiteFileRepository
from app.services.file_validation_service import FileValidationError, get_mime_type
from app.services.google_drive_service import GoogleDriveService
from app.services.zip_service import ExtractedFile, extract_zip

logger = structlog.get_logger()


class DeploymentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self._file_repo = WebsiteFileRepository(db)
        self._meta_repo = FileMetadataRepository(db)

    async def deploy_zip(
        self, site: Site, zip_bytes: bytes, access_token: str
    ) -> Deployment:
        deployment = Deployment(
            site_id=site.id,
            status="pending",
        )
        self.db.add(deployment)
        self.db.flush()

        try:
            files = extract_zip(zip_bytes)
            await self._upload_files(site, files, access_token)
            deployment.status = "success"
            deployment.finished_at = datetime.now(timezone.utc)
            site.status = "deployed"
            self.db.commit()
            logger.info("deployment_success", site_id=str(site.id), files=len(files))
        except FileValidationError as exc:
            deployment.status = "failed"
            deployment.error_message = str(exc)
            deployment.finished_at = datetime.now(timezone.utc)
            self.db.commit()
            raise
        except Exception as exc:
            deployment.status = "failed"
            deployment.error_message = str(exc)
            deployment.finished_at = datetime.now(timezone.utc)
            self.db.commit()
            logger.error("deployment_failed", site_id=str(site.id), error=str(exc))
            raise

        return deployment

    async def _ensure_drive_folder(self, site: Site, drive: GoogleDriveService) -> str:
        """Return the site's Drive folder ID, creating one if none exists yet."""
        if site.drive_folder_id:
            return site.drive_folder_id
        folder = await drive.create_folder(name=f"axithor-{site.subdomain}")
        site.drive_folder_id = folder.id
        self.db.flush()
        return folder.id

    async def _upload_files(
        self, site: Site, files: list[ExtractedFile], access_token: str
    ) -> None:
        drive = GoogleDriveService(access_token)

        folder_id = await self._ensure_drive_folder(site, drive)

        # Wipe existing file records so redeployment is clean
        self._file_repo.delete_by_site(site.id)

        for ef in files:
            mime_type = get_mime_type(ef.path)
            filename = ef.path.replace("/", "_")  # flat layout in Drive folder

            drive_id = await drive.upload_file(
                folder_id=folder_id,
                filename=filename,
                content=ef.content,
                mime_type=mime_type,
            )

            self._file_repo.create(
                site_id=site.id,
                path=ef.path,
                provider_file_id=drive_id,
                mime_type=mime_type,
                file_size=ef.size,
            )

            self._meta_repo.upsert(
                site_id=site.id,
                path=ef.path,
                provider_file_id=drive_id,
                checksum=ef.checksum,
            )

    def get_deployments(self, site_id: uuid.UUID) -> list[Deployment]:
        return (
            self.db.query(Deployment)
            .filter(Deployment.site_id == site_id)
            .order_by(Deployment.created_at.desc())
            .all()
        )

    def get_deployment(self, deployment_id: uuid.UUID) -> Deployment | None:
        return self.db.query(Deployment).filter(Deployment.id == deployment_id).first()
