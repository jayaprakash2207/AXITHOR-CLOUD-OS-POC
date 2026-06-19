from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.api import api_router
from app.api.v1.routes import serve
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.auth import AuthContextMiddleware
from app.middleware.subdomain import SubdomainRoutingMiddleware

configure_logging()

app = FastAPI(title=settings.app_name, version=settings.app_version)

# Subdomain routing must be outermost so it can rewrite paths before auth/session
if settings.base_domain:
    app.add_middleware(SubdomainRoutingMiddleware, base_domain=settings.base_domain)

app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key)
app.add_middleware(AuthContextMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# Internal serving router — used by SubdomainRoutingMiddleware rewrites
app.include_router(serve.router, prefix="/serve", tags=["serve"])


@app.get("/healthz", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
