"""Module 6 — Sync Engine (Google Drive webhooks)"""
from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.site_repository import SiteRepository
from app.repositories.storage_repository import StorageRepository
from app.schemas.sync import SyncEventRead, WatchChannelCreate, WatchChannelRead
from app.services.google_drive_service import GoogleDriveService
from app.services.sync_service import SyncService

logger = structlog.get_logger()

router = APIRouter()


@router.post("/drive/webhook", status_code=status.HTTP_200_OK, include_in_schema=False)
async def drive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    raw_headers = dict(request.headers)
    resource_state = raw_headers.get("x-goog-resource-state", "")

    if resource_state == "sync":
        return {"status": "sync_ack"}

    body = await request.body()
    svc = SyncService(db)
    event = svc.ingest_drive_webhook(
        headers=raw_headers,
        raw_body=body.decode("utf-8", errors="replace"),
    )

    background_tasks.add_task(_process_event_bg, event.id)
    return {"status": "accepted", "event_id": str(event.id)}


async def _process_event_bg(event_id: uuid.UUID) -> None:
    """Background task: re-open DB session and process the event."""
    from app.db.session import SessionLocal

    with SessionLocal() as db:
        from app.models.sync_event import SyncEvent
        from app.models.storage_account import StorageAccount

        event = db.query(SyncEvent).filter(SyncEvent.id == event_id).first()
        if event is None:
            return

        if event.site_id:
            from app.models.site import Site

            site = db.query(Site).filter(Site.id == event.site_id).first()
            if site:
                account = (
                    db.query(StorageAccount)
                    .filter(
                        StorageAccount.user_id == site.user_id,
                        StorageAccount.provider == "google_drive",
                    )
                    .first()
                )
                token_map = {str(site.id): account.access_token} if account else {}
            else:
                token_map = {}
        else:
            token_map = {}

        svc = SyncService(db)
        await svc._process_event(event, token_map)


@router.post("/sites/{site_id}/watch", response_model=WatchChannelRead)
async def register_watch(
    site_id: uuid.UUID,
    body: WatchChannelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WatchChannelRead:
    from app.core.config import settings

    site_repo = SiteRepository(db)
    site = site_repo.get_by_id(site_id)
    if site is None or site.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    storage_repo = StorageRepository(db)
    account = storage_repo.get_by_user_and_provider(current_user.id, "google_drive")
    if not account or not account.access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Drive not connected.",
        )

    channel_id = body.channel_id or str(uuid.uuid4())
    webhook_url = f"{settings.backend_base_url}/api/v1/sync/drive/webhook"

    drive = GoogleDriveService(account.access_token)
    result = await drive.watch_folder(
        folder_id=site.drive_folder_id,
        channel_id=channel_id,
        webhook_url=webhook_url,
        token=str(site.id),
    )

    return WatchChannelRead(
        channel_id=result.get("id", channel_id),
        resource_id=result.get("resourceId", ""),
        expiration=result.get("expiration", ""),
        site_id=site.id,
    )


@router.get("/sites/{site_id}/sync-events", response_model=list[SyncEventRead])
def list_sync_events(
    site_id: uuid.UUID,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SyncEventRead]:
    site_repo = SiteRepository(db)
    site = site_repo.get_by_id(site_id)
    if site is None or site.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    svc = SyncService(db)
    events = svc.list_events(site_id=site_id, limit=limit)
    return [SyncEventRead.model_validate(e) for e in events]
