from __future__ import annotations

from datetime import datetime, timedelta, timezone

import structlog
from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.integrations.google_oauth import oauth
from app.models.user import User
from app.repositories.storage_repository import StorageRepository
from app.schemas.storage import StorageAccountRead, StorageUsageRead
from app.services.google_drive_storage_service import GoogleDriveStorageService

logger = structlog.get_logger()

router = APIRouter()


@router.get("/google/login")
async def connect_google_drive(request: Request, current_user: User = Depends(get_current_user)):
    return await oauth.google_drive.authorize_redirect(
        request,
        settings.google_drive_redirect_uri,
        access_type="offline",
        prompt="consent",
    )


@router.get("/google/callback")
async def google_drive_callback(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        token = await oauth.google_drive.authorize_access_token(request)
    except OAuthError as exc:
        logger.error("google_drive_oauth_error", error=str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Google Drive OAuth failed: {exc}") from exc
    except Exception as exc:
        logger.error("google_drive_callback_error", error=str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google Drive authorization failed") from exc

    refresh_token = token.get("refresh_token")
    access_token = token.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google Drive access token was not returned")

    expires_in = token.get("expires_in")
    token_expires_at = (
        datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
        if expires_in else None
    )

    quota_str = None
    try:
        storage_service = GoogleDriveStorageService(access_token, refresh_token)
        quota, _ = await storage_service.get_quota_and_metadata()
        quota_str = str(quota)
    except Exception as exc:
        logger.warning("google_drive_quota_fetch_failed", error=str(exc))

    storage_repo = StorageRepository(db)
    storage_repo.upsert_google_drive(
        user_id=current_user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        quota=quota_str,
        token_expires_at=token_expires_at,
    )
    db.commit()
    return RedirectResponse(url=f"{settings.frontend_base_url}/dashboard?storage=connected")


@router.get("/me", response_model=StorageAccountRead)
def get_storage_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = StorageRepository(db).get_by_user_and_provider(current_user.id, "google_drive")
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storage account not connected")

    return StorageAccountRead(
        id=account.id,
        user_id=account.user_id,
        provider=account.provider,
        quota=account.quota,
        created_at=account.created_at,
    )


@router.get("/usage", response_model=StorageUsageRead)
async def get_storage_usage(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = StorageRepository(db).get_by_user_and_provider(current_user.id, "google_drive")
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storage account not connected")

    storage_service = GoogleDriveStorageService(account.access_token, account.refresh_token)
    try:
        quota, metadata = await storage_service.get_quota_and_metadata()
    except Exception as exc:
        if account.refresh_token:
            try:
                new_access_token, new_refresh_token, _ = await storage_service.refresh_access_token()
                account.access_token = new_access_token
                account.refresh_token = new_refresh_token
                db.commit()
                quota, metadata = await storage_service.get_quota_and_metadata()
            except Exception as refresh_exc:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unable to refresh Drive token") from refresh_exc
        else:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unable to retrieve Drive usage") from exc

    account.quota = str(quota)
    db.commit()
    return StorageUsageRead(storage_quota=quota, drive_metadata=metadata)


@router.post("/disconnect")
async def disconnect_storage(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    storage_repo = StorageRepository(db)
    account = storage_repo.get_by_user_and_provider(current_user.id, "google_drive")
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storage account not connected")

    service = GoogleDriveStorageService(account.access_token, account.refresh_token)
    await service.disconnect()
    storage_repo.delete(account)
    db.commit()
    return {"message": "Storage account disconnected"}