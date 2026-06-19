from __future__ import annotations

from fastapi import Request

from app.core.config import settings
from app.integrations.google_oauth import oauth
from app.core.security import create_token_pair
from app.models.user import User


class AuthService:
    def issue_session_tokens(self, user: User):
        return create_token_pair(str(user.id), {"email": user.email})

    def build_google_authorize_url(self, request: Request):
        return oauth.google.authorize_redirect(request, settings.google_oauth_redirect_uri)
