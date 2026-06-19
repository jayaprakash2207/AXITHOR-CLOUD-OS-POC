from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.oauth_repository import OAuthRepository
from app.repositories.site_repository import SiteRepository
from app.services.google_drive_service import GoogleDriveService


class SiteService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.site_repository = SiteRepository(db)
        self.oauth_repository = OAuthRepository(db)

    def list_sites(self, user_id):
        return self.site_repository.list_for_user(user_id)

    async def get_site_files(self, site_id, user_id):
        site = self.site_repository.get_by_id(site_id)
        if not site or site.user_id != user_id:
            raise ValueError("Site not found")

        oauth_account = self.oauth_repository.get_by_user_id(user_id, "google")
        # Note: In a real app, you would handle token refresh here if expired.
        if not oauth_account or not oauth_account.access_token:
            raise ValueError("Google account not connected or missing permissions")

        drive_service = GoogleDriveService(oauth_account.access_token)
        return await drive_service.list_site_files(site.drive_folder_id)

    def create_site(self, *, user_id, name: str, subdomain: str, drive_folder_id: str | None = None, custom_domain: str | None = None):
        existing = self.site_repository.get_by_subdomain(subdomain)
        if existing is not None:
            raise ValueError("Subdomain already exists")
        return self.site_repository.create(
            user_id=user_id,
            name=name,
            subdomain=subdomain,
            drive_folder_id=drive_folder_id,
            custom_domain=custom_domain,
        )
