from fastapi import APIRouter

from app.api.v1.routes import auth, cache, deploy, domains, health, metadata, sites, storage, sync

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(storage.router, prefix="/storage", tags=["storage"])

# Module 3 — Deployment Engine
api_router.include_router(deploy.router, prefix="/sites", tags=["deploy"])

# Module 4 — Domain management
api_router.include_router(domains.router, tags=["domains"])

# Module 5 — Metadata Engine
api_router.include_router(metadata.router, tags=["metadata"])

# Module 6 — Sync Engine
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])

# Module 7 — Cache Layer
api_router.include_router(cache.router, tags=["cache"])
