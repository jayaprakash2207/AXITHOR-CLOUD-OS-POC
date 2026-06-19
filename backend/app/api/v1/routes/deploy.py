"""Module 3 — Website Deployment Engine"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.site_repository import SiteRepository
from app.repositories.storage_repository import StorageRepository
from app.repositories.website_file_repository import WebsiteFileRepository
from app.schemas.deploy import DeployedFileRead, DeploymentRead, DeploymentResultRead
from app.services.deployment_service import DeploymentService
from app.services.file_validation_service import FileValidationError

router = APIRouter()

MAX_ZIP_SIZE = 100 * 1024 * 1024  # 100 MB


def _get_access_token(user: User, db: Session) -> str:
    storage_repo = StorageRepository(db)
    account = storage_repo.get_by_user_and_provider(user.id, "google_drive")
    if account is None or not account.access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Drive not connected. Connect storage first.",
        )
    return account.access_token


@router.post(
    "/{site_id}/deploy",
    response_model=DeploymentResultRead,
    status_code=status.HTTP_201_CREATED,
)
async def deploy_zip(
    site_id: uuid.UUID,
    zip_file: UploadFile = File(..., description="ZIP archive of static website"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeploymentResultRead:
    site_repo = SiteRepository(db)
    site = site_repo.get_by_id(site_id)
    if site is None or site.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    _ALLOWED_ZIP_TYPES = {
        "application/zip",
        "application/x-zip-compressed",
        "application/x-zip",
        "application/octet-stream",
    }
    if zip_file.content_type not in _ALLOWED_ZIP_TYPES and not (zip_file.filename or "").endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only ZIP files are accepted.",
        )

    zip_bytes = await zip_file.read()
    if len(zip_bytes) > MAX_ZIP_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"ZIP file exceeds the 100 MB limit.",
        )

    access_token = _get_access_token(current_user, db)

    try:
        svc = DeploymentService(db)
        deployment = await svc.deploy_zip(site, zip_bytes, access_token)
    except FileValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deployment failed: {exc}",
        ) from exc

    file_repo = WebsiteFileRepository(db)
    deployed_files = file_repo.get_by_site(site.id)

    return DeploymentResultRead(
        site_id=site.id,
        status=deployment.status,
        files_deployed=len(deployed_files),
        files=[DeployedFileRead.model_validate(f) for f in deployed_files],
        deployment_id=deployment.id,
        created_at=deployment.created_at,
    )


@router.get("/{site_id}/deployments", response_model=list[DeploymentRead])
def list_deployments(
    site_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DeploymentRead]:
    site_repo = SiteRepository(db)
    site = site_repo.get_by_id(site_id)
    if site is None or site.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    svc = DeploymentService(db)
    deployments = svc.get_deployments(site_id)
    return [DeploymentRead.model_validate(d) for d in deployments]


@router.get("/{site_id}/files", response_model=list[DeployedFileRead])
def list_site_files(
    site_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DeployedFileRead]:
    site_repo = SiteRepository(db)
    site = site_repo.get_by_id(site_id)
    if site is None or site.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    file_repo = WebsiteFileRepository(db)
    files = file_repo.get_by_site(site_id)
    return [DeployedFileRead.model_validate(f) for f in files]
