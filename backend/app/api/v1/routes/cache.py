"""Module 7 — Cloudflare Cache Layer"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.site_repository import SiteRepository
from app.services.cloudflare_service import CloudflareService

router = APIRouter()


def _get_cf_service() -> CloudflareService:
    if not settings.cloudflare_api_token or not settings.cloudflare_zone_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cloudflare integration is not configured.",
        )
    return CloudflareService(
        api_token=settings.cloudflare_api_token,
        zone_id=settings.cloudflare_zone_id,
    )


@router.post("/sites/{site_id}/cache/purge")
async def purge_site_cache(
    site_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    site_repo = SiteRepository(db)
    site = site_repo.get_by_id(site_id)
    if site is None or site.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    cf = _get_cf_service()
    base_domain = settings.base_domain
    result = await cf.purge_subdomain(site.subdomain, base_domain)
    return {"status": "purged", "subdomain": site.subdomain, "result": result}


@router.post("/cache/purge-all")
async def purge_all_cache(
    current_user: User = Depends(get_current_user),
) -> dict:
    cf = _get_cf_service()
    result = await cf.purge_everything()
    return {"status": "purged_all", "result": result}


@router.get("/cache/rules")
async def list_cache_rules(
    current_user: User = Depends(get_current_user),
) -> dict:
    cf = _get_cf_service()
    rules = await cf.list_cache_rules()
    return {"rules": rules}


@router.get("/cache/analytics")
async def get_cache_analytics(
    since_hours: int = 24,
    current_user: User = Depends(get_current_user),
) -> dict:
    cf = _get_cf_service()
    data = await cf.get_cache_analytics(since_hours=since_hours)
    return data
