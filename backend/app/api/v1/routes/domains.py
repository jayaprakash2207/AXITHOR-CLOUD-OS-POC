"""Module 4 — Domain management"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.domain_repository import DomainRepository
from app.repositories.site_repository import SiteRepository
from app.schemas.domain import DomainCreate, DomainRead, DomainUpdate

router = APIRouter()


def _get_owned_site(site_id: uuid.UUID, user: User, db: Session):
    repo = SiteRepository(db)
    site = repo.get_by_id(site_id)
    if site is None or site.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    return site


@router.post(
    "/sites/{site_id}/domains",
    response_model=DomainRead,
    status_code=status.HTTP_201_CREATED,
)
def add_domain(
    site_id: uuid.UUID,
    body: DomainCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DomainRead:
    site = _get_owned_site(site_id, current_user, db)
    domain_repo = DomainRepository(db)

    existing = domain_repo.get_by_domain(body.domain)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Domain '{body.domain}' is already registered.",
        )

    record = domain_repo.create(site_id=site.id, domain=body.domain)
    db.commit()
    return DomainRead.model_validate(record)


@router.get("/sites/{site_id}/domains", response_model=list[DomainRead])
def list_domains(
    site_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DomainRead]:
    site = _get_owned_site(site_id, current_user, db)
    domain_repo = DomainRepository(db)
    return [DomainRead.model_validate(d) for d in domain_repo.get_by_site(site.id)]


@router.patch("/domains/{domain_id}", response_model=DomainRead)
def update_domain_ssl(
    domain_id: uuid.UUID,
    body: DomainUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DomainRead:
    domain_repo = DomainRepository(db)
    record = domain_repo.get_by_id(domain_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")

    site_repo = SiteRepository(db)
    site = site_repo.get_by_id(record.site_id)
    if site is None or site.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    updated = domain_repo.update_ssl_status(domain_id, body.ssl_status)
    db.commit()
    return DomainRead.model_validate(updated)


@router.delete("/domains/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_domain(
    domain_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    domain_repo = DomainRepository(db)
    record = domain_repo.get_by_id(domain_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")

    site_repo = SiteRepository(db)
    site = site_repo.get_by_id(record.site_id)
    if site is None or site.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    domain_repo.delete(domain_id)
    db.commit()
