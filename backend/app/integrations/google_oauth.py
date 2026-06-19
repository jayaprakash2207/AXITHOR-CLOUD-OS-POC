from __future__ import annotations

from authlib.integrations.starlette_client import OAuth

from app.core.config import settings

oauth = OAuth()
oauth.register(
    name="google_auth",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    api_base_url="https://www.googleapis.com/oauth2/v2/",
    client_kwargs={"scope": "openid email profile"},
)
oauth.register(
    name="google_drive",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    api_base_url="https://www.googleapis.com/drive/v3/",
    client_kwargs={
        "scope": "https://www.googleapis.com/auth/drive.metadata.readonly https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/drive.file",
        "token_endpoint_auth_method": "client_secret_post",
    },
)