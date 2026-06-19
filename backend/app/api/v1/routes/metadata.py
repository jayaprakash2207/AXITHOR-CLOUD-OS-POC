"""Module 5 — Metadata Engine"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.site_repository import SiteRepository
from app.repositories.storage_repository import StorageRepository
from app.schemas.metadata import FileMetadataRead, FileMetadataSyncResult
from app.services.metadata_service import MetadataService

router = APIRouter()


def _get_owned_site(site_id: uuid.UUID, user: User, db: Session):
    repo = SiteRepository(db)
    site = repo.get_by_id(site_id)
    if site is None or site.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    return site


@router.get("/sites/{site_id}/metadata", response_model=list[FileMetadataRead])
def get_site_metadata(
    site_id: uuid.UUID,
    path_prefix: str | None = Query(default=None, description="Filter by path prefix"),
    all_versions: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[FileMetadataRead]:
    site = _get_owned_site(site_id, current_user, db)
    svc = MetadataService(db)

    if path_prefix:
        records = svc.search(site.id, path_prefix)
    elif all_versions:
        records = svc.get_all_for_site(site.id)
    else:
        records = svc.get_latest_for_site(site.id)

    return [FileMetadataRead.model_validate(r) for r in records]


@router.get(
    "/sites/{site_id}/metadata/file",
    response_model=list[FileMetadataRead],
)
def get_file_history(
    site_id: uuid.UUID,
    path: str = Query(..., description="Exact file path"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[FileMetadataRead]:
    site = _get_owned_site(site_id, current_user, db)
    svc = MetadataService(db)
    records = svc.get_history(site.id, path)
    return [FileMetadataRead.model_validate(r) for r in records]


@router.get("/sites/{site_id}/metadata/validate")
def validate_checksum(
    site_id: uuid.UUID,
    path: str = Query(...),
    checksum: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    site = _get_owned_site(site_id, current_user, db)
    svc = MetadataService(db)
    valid = svc.validate_checksum(site.id, path, checksum)
    return {"path": path, "checksum": checksum, "valid": valid}


@router.post(
    "/sites/{site_id}/metadata/sync",
    response_model=FileMetadataSyncResult,
)
async def sync_metadata(
    site_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileMetadataSyncResult:
    site = _get_owned_site(site_id, current_user, db)

    storage_repo = StorageRepository(db)
    account = storage_repo.get_by_user_and_provider(current_user.id, "google_drive")
    if not account or not account.access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Drive not connected.",
        )

    svc = MetadataService(db)
    return await svc.sync_from_drive(site, account.access_token)
