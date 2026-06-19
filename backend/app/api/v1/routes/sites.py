from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.site import SiteCreateRequest, SiteRead
from app.services.site_service import SiteService

router = APIRouter()


@router.get("", response_model=list[SiteRead])
def list_sites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = SiteService(db)
    sites = service.list_sites(current_user.id)
    return [
        SiteRead(
            id=site.id,
            user_id=site.user_id,
            name=site.name,
            subdomain=site.subdomain,
            drive_folder_id=site.drive_folder_id,
            custom_domain=site.custom_domain,
            status=site.status,
            created_at=site.created_at,
            updated_at=site.updated_at,
        )
        for site in sites
    ]


@router.post("", response_model=SiteRead, status_code=status.HTTP_201_CREATED)
def create_site(payload: SiteCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = SiteService(db)
    try:
        site = service.create_site(
            user_id=current_user.id,
            name=payload.name,
            subdomain=payload.subdomain,
            drive_folder_id=payload.drive_folder_id,
            custom_domain=payload.custom_domain,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return SiteRead(
        id=site.id,
        user_id=site.user_id,
        name=site.name,
        subdomain=site.subdomain,
        drive_folder_id=site.drive_folder_id,
        custom_domain=site.custom_domain,
        status=site.status,
        created_at=site.created_at,
        updated_at=site.updated_at,
    )


@router.get("/{site_id}", response_model=SiteRead)
def get_site(
    site_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.repositories.site_repository import SiteRepository

    repo = SiteRepository(db)
    site = repo.get_by_id(site_id)
    if site is None or site.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    return SiteRead(
        id=site.id,
        user_id=site.user_id,
        name=site.name,
        subdomain=site.subdomain,
        drive_folder_id=site.drive_folder_id,
        custom_domain=site.custom_domain,
        status=site.status,
        created_at=site.created_at,
        updated_at=site.updated_at,
    )


