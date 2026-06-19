from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class GoogleOAuthStartResponse(BaseModel):
    authorization_url: str


class OAuthCallbackResponse(BaseModel):
    redirect_url: str


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    picture: str | None
    created_at: datetime
    updated_at: datetime


class AuthSessionResponse(BaseModel):
    user: UserRead


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
