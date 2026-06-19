from __future__ import annotations

import structlog
from sqlalchemy.orm import Session

from app.models.site import Site
from app.models.website_file import WebsiteFile
from app.services.google_drive_service import GoogleDriveService

logger = structlog.get_logger()

_INDEX_FALLBACKS = ["index.html", "index.htm"]


class SiteNotFoundError(Exception):
    pass


class SubdomainService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def resolve_site(self, subdomain: str) -> Site:
        site = (
            self.db.query(Site)
            .filter(Site.subdomain == subdomain, Site.status == "deployed")
            .first()
        )
        if site is None:
            raise SiteNotFoundError(f"No deployed site found for subdomain '{subdomain}'")
        return site

    def resolve_file(self, site: Site, path: str) -> WebsiteFile | None:
        clean = path.lstrip("/") or "index.html"
        record = (
            self.db.query(WebsiteFile)
            .filter(WebsiteFile.site_id == site.id, WebsiteFile.path == clean)
            .first()
        )
        if record:
            return record

        # Try index.html fallback for directory-style paths
        for candidate in _INDEX_FALLBACKS:
            if not clean.endswith("/"):
                candidate_path = f"{clean}/{candidate}"
            else:
                candidate_path = f"{clean}{candidate}"
            record = (
                self.db.query(WebsiteFile)
                .filter(WebsiteFile.site_id == site.id, WebsiteFile.path == candidate_path)
                .first()
            )
            if record:
                return record

        # Final fallback: root index.html (SPA mode)
        return (
            self.db.query(WebsiteFile)
            .filter(WebsiteFile.site_id == site.id, WebsiteFile.path == "index.html")
            .first()
        )

    async def fetch_file_content(self, file: WebsiteFile, access_token: str) -> bytes:
        drive = GoogleDriveService(access_token)
        return await drive.download_file(file.provider_file_id)
