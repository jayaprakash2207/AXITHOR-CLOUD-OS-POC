from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class AuthContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.state.access_token = request.cookies.get(settings.access_token_cookie_name)
        request.state.refresh_token = request.cookies.get(settings.refresh_token_cookie_name)
        return await call_next(request)