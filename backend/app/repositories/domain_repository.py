from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.domain import Domain
from app.repositories.base import BaseRepository


class DomainRepository(BaseRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def create(self, site_id: uuid.UUID, domain: str) -> Domain:
        record = Domain(site_id=site_id, domain=domain)
        self.db.add(record)
        self.db.flush()
        return record

    def get_by_id(self, domain_id: uuid.UUID) -> Domain | None:
        return self.db.query(Domain).filter(Domain.id == domain_id).first()

    def get_by_domain(self, domain: str) -> Domain | None:
        return self.db.query(Domain).filter(Domain.domain == domain).first()

    def get_by_site(self, site_id: uuid.UUID) -> list[Domain]:
        return self.db.query(Domain).filter(Domain.site_id == site_id).all()

    def update_ssl_status(self, domain_id: uuid.UUID, ssl_status: str) -> Domain | None:
        record = self.get_by_id(domain_id)
        if record is None:
            return None
        record.ssl_status = ssl_status
        self.db.flush()
        return record

    def delete(self, domain_id: uuid.UUID) -> bool:
        record = self.get_by_id(domain_id)
        if record is None:
            return False
        self.db.delete(record)
        self.db.flush()
        return True
