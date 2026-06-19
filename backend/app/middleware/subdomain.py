"""Middleware that intercepts subdomain requests and delegates to SubdomainService."""
from __future__ import annotations

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger()

_API_PREFIXES = ("/api/", "/healthz", "/docs", "/openapi", "/redoc")


class SubdomainRoutingMiddleware(BaseHTTPMiddleware):
    """
    Intercepts requests whose Host header matches <subdomain>.<base_domain>
    and proxies them to the /serve/<subdomain>/<path> handler.
    """

    def __init__(self, app, base_domain: str) -> None:
        super().__init__(app)
        self.base_domain = base_domain.lower()

    async def dispatch(self, request: Request, call_next) -> Response:
        host = request.headers.get("host", "").split(":")[0].lower()
        suffix = f".{self.base_domain}"

        if not host.endswith(suffix):
            return await call_next(request)

        subdomain = host[: -len(suffix)]
        if not subdomain:
            return await call_next(request)

        # Skip API, health, and docs paths
        path = request.url.path
        if any(path.startswith(p) for p in _API_PREFIXES):
            return await call_next(request)

        asset_path = path.lstrip("/")
        serve_url = f"/serve/{subdomain}/{asset_path}" if asset_path else f"/serve/{subdomain}"

        # Rewrite the path and dispatch internally
        scope = dict(request.scope)
        scope["path"] = serve_url
        scope["raw_path"] = serve_url.encode()
        rewritten = Request(scope, request.receive)
        return await call_next(rewritten)
