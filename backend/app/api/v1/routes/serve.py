"""Module 4.5 — Static Asset Resolution Engine (serve router)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import structlog
from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.asset_resolution_service import (
    AssetNotFoundError,
    AssetResolutionError,
    build_cache_headers,
    check_not_modified,
    make_error_html,
    sanitize_path,
    stream_drive_file,
)
from app.services.subdomain_service import SiteNotFoundError, SubdomainService
from app.utils.mime_types import get_mime_type

logger = structlog.get_logger()

router = APIRouter()

_HTML_404 = make_error_html(404, "Not Found", "The page or asset you requested does not exist.")
_HTML_500 = make_error_html(500, "Server Error", "Something went wrong on our end.")
_HTML_503 = make_error_html(503, "Service Unavailable", "Storage is not configured.")


async def _resolve_access_token(db: Session) -> str | None:
    from app.models.storage_account import StorageAccount
    from app.services.google_drive_storage_service import GoogleDriveStorageService

    account = db.query(StorageAccount).filter(StorageAccount.provider == "google_drive").first()
    if not account:
        return None

    # Proactively refresh if the token is expired or expires within 60 s
    expires_at = account.token_expires_at
    if account.refresh_token and expires_at is not None:
        if expires_at <= datetime.now(timezone.utc) + timedelta(seconds=60):
            try:
                svc = GoogleDriveStorageService(account.access_token, account.refresh_token)
                new_token, new_refresh, new_expires = await svc.refresh_access_token()
                account.access_token = new_token
                if new_refresh:
                    account.refresh_token = new_refresh
                account.token_expires_at = new_expires
                db.commit()
                return new_token
            except Exception:
                logger.warning("token_refresh_failed_serving_with_stale")

    return account.access_token


def _html_response(html: str, status_code: int) -> Response:
    return Response(content=html, status_code=status_code, media_type="text/html; charset=utf-8")


@router.get("/{subdomain}/{path:path}", include_in_schema=False)
@router.get("/{subdomain}", include_in_schema=False)
async def serve_site(
    subdomain: str,
    request: Request,
    path: str = "",
    db: Session = Depends(get_db),
) -> Response:
    # ------------------------------------------------------------------ #
    # 1. Security — sanitize the requested path                           #
    # ------------------------------------------------------------------ #
    clean_path = sanitize_path(path)
    if clean_path is None:
        logger.warning("path_traversal_attempt", raw_path=path, subdomain=subdomain,
                       client=request.client.host if request.client else "unknown")
        return _html_response(
            make_error_html(400, "Bad Request", "Invalid path."), 400
        )

    # ------------------------------------------------------------------ #
    # 2. Resolve subdomain → site                                         #
    # ------------------------------------------------------------------ #
    svc = SubdomainService(db)
    try:
        site = svc.resolve_site(subdomain)
    except Exception:
        return _html_response(_HTML_404, 404)

    # ------------------------------------------------------------------ #
    # 3. Resolve path → file record (with SPA index.html fallback)        #
    # ------------------------------------------------------------------ #
    file_record = svc.resolve_file(site, clean_path)
    if file_record is None:
        logger.info("asset_not_found", subdomain=subdomain, path=clean_path)
        return _html_response(_HTML_404, 404)

    # ------------------------------------------------------------------ #
    # 4. Conditional GET — ETag check (304 Not Modified)                  #
    # ------------------------------------------------------------------ #
    mime = get_mime_type(file_record.path)
    cache_headers = build_cache_headers(file_record, mime)

    if check_not_modified(file_record, request.headers.get("if-none-match")):
        return Response(status_code=304, headers={
            "ETag": cache_headers["ETag"],
            "Cache-Control": cache_headers["Cache-Control"],
        })

    # ------------------------------------------------------------------ #
    # 5. Resolve storage access token                                      #
    # ------------------------------------------------------------------ #
    access_token = await _resolve_access_token(db)
    if not access_token:
        logger.error("storage_not_configured", subdomain=subdomain)
        return _html_response(_HTML_503, 503)

    # ------------------------------------------------------------------ #
    # 6. Stream file from Google Drive                                     #
    # ------------------------------------------------------------------ #
    logger.info("serving_asset", subdomain=subdomain, path=clean_path, mime=mime)

    try:
        return StreamingResponse(
            stream_drive_file(file_record.provider_file_id, access_token),
            media_type=mime,
            headers=cache_headers,
        )
    except AssetNotFoundError:
        logger.error("drive_file_missing", provider_file_id=file_record.provider_file_id,
                     path=clean_path)
        return _html_response(_HTML_404, 404)
    except AssetResolutionError as exc:
        logger.error("drive_error", error=str(exc), path=clean_path)
        return _html_response(_HTML_500, 500)
    except Exception as exc:
        logger.error("unexpected_serve_error", error=str(exc), path=clean_path)
        return _html_response(_HTML_500, 500)
