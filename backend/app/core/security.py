from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from jose import JWTError, jwt

from app.core.config import settings

TokenKind = Literal["access", "refresh"]


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime


def _build_payload(subject: str, kind: TokenKind, expires_at: datetime, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"sub": subject, "type": kind, "exp": expires_at, "iat": datetime.now(timezone.utc)}
    if extra:
        payload.update(extra)
    return payload


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> tuple[str, datetime]:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    token = jwt.encode(_build_payload(subject, "access", expires_at, extra), settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, expires_at


def create_refresh_token(subject: str, extra: dict[str, Any] | None = None) -> tuple[str, datetime]:
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    token = jwt.encode(_build_payload(subject, "refresh", expires_at, extra), settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, expires_at


def create_token_pair(subject: str, extra: dict[str, Any] | None = None) -> TokenPair:
    access_token, access_expires_at = create_access_token(subject, extra)
    refresh_token, refresh_expires_at = create_refresh_token(subject, extra)
    return TokenPair(access_token, refresh_token, access_expires_at, refresh_expires_at)


def decode_token(token: str, expected_kind: TokenKind) -> dict[str, Any]:
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    if payload.get("type") != expected_kind:
        raise JWTError("Invalid token type")
    return payload