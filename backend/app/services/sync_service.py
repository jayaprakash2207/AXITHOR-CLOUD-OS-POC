from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy.orm import Session

from app.models.site import Site
from app.models.sync_event import SyncEvent
from app.services.metadata_service import MetadataService

logger = structlog.get_logger()

MAX_RETRY = 3


class SyncService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------ #
    # Webhook ingestion                                                    #
    # ------------------------------------------------------------------ #

    def ingest_drive_webhook(
        self,
        headers: dict[str, str],
        raw_body: str = "",
    ) -> SyncEvent:
        resource_id = headers.get("x-goog-resource-id", "")
        resource_state = headers.get("x-goog-resource-state", "")
        channel_token = headers.get("x-goog-channel-token", "")

        site = self._resolve_site_from_token(channel_token)

        event = SyncEvent(
            site_id=site.id if site else None,
            event_type=f"drive.{resource_state}",
            provider_resource_id=resource_id,
            payload=json.dumps({"headers": headers, "body": raw_body}),
            status="pending",
        )
        self.db.add(event)
        self.db.commit()
        logger.info("sync_event_ingested", event_id=str(event.id), type=event.event_type)
        return event

    def _resolve_site_from_token(self, token: str) -> Site | None:
        """Token is the site_id we set when registering the watch channel."""
        if not token:
            return None
        try:
            site_id = uuid.UUID(token)
        except ValueError:
            return None
        return self.db.query(Site).filter(Site.id == site_id).first()

    # ------------------------------------------------------------------ #
    # Processing                                                           #
    # ------------------------------------------------------------------ #

    async def process_pending(self, access_token_map: dict[str, str]) -> list[SyncEvent]:
        pending = (
            self.db.query(SyncEvent)
            .filter(SyncEvent.status == "pending", SyncEvent.retry_count < MAX_RETRY)
            .all()
        )
        results = []
        for event in pending:
            await self._process_event(event, access_token_map)
            results.append(event)
        return results

    async def _process_event(
        self, event: SyncEvent, access_token_map: dict[str, str]
    ) -> None:
        if event.site_id is None:
            event.status = "skipped"
            event.processed_at = datetime.now(timezone.utc)
            self.db.commit()
            return

        site_id_str = str(event.site_id)
        access_token = access_token_map.get(site_id_str)
        if not access_token:
            event.status = "skipped"
            event.error = "No access token available for site"
            event.processed_at = datetime.now(timezone.utc)
            self.db.commit()
            return

        try:
            site = self.db.query(Site).filter(Site.id == event.site_id).first()
            if site is None:
                raise ValueError("Site not found")

            meta_svc = MetadataService(self.db)
            await meta_svc.sync_from_drive(site, access_token)

            event.status = "processed"
            event.processed_at = datetime.now(timezone.utc)
            logger.info("sync_event_processed", event_id=str(event.id))
        except Exception as exc:
            event.retry_count += 1
            event.error = str(exc)
            if event.retry_count >= MAX_RETRY:
                event.status = "failed"
            logger.error(
                "sync_event_error",
                event_id=str(event.id),
                error=str(exc),
                retry=event.retry_count,
            )
        self.db.commit()

    # ------------------------------------------------------------------ #
    # Event log                                                            #
    # ------------------------------------------------------------------ #

    def list_events(
        self, site_id: uuid.UUID | None = None, limit: int = 50
    ) -> list[SyncEvent]:
        q = self.db.query(SyncEvent)
        if site_id:
            q = q.filter(SyncEvent.site_id == site_id)
        return q.order_by(SyncEvent.created_at.desc()).limit(limit).all()
