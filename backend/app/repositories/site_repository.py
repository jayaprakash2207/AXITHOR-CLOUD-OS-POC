from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.site import Site
from app.repositories.base import BaseRepository


class SiteRepository(BaseRepository):
    def list_for_user(self, user_id: UUID) -> list[Site]:
        stmt = select(Site).where(Site.user_id == user_id).order_by(Site.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, site_id: UUID) -> Site | None:
        return self.db.get(Site, site_id)

    def get_by_subdomain(self, subdomain: str) -> Site | None:
        return self.db.scalar(select(Site).where(Site.subdomain == subdomain))

    def create(self, *, user_id: UUID, name: str, subdomain: str, drive_folder_id: str | None = None, custom_domain: str | None = None) -> Site:
        site = Site(
            user_id=user_id,
            name=name,
            subdomain=subdomain,
            drive_folder_id=drive_folder_id,
            custom_domain=custom_domain,
        )
        self.db.add(site)
        self.db.flush()
        return site
