from __future__ import annotations

import uuid as _uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from jose import JWTError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.db.session import get_db
from app.integrations.google_oauth import oauth
from app.models.user import User
from app.repositories.oauth_repository import OAuthRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AuthSessionResponse, GoogleOAuthStartResponse, TokenResponse, UserRead

router = APIRouter()


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str, access_expires_at, refresh_expires_at) -> None:
    response.set_cookie(
        key=settings.access_token_cookie_name,
        value=access_token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        expires=access_expires_at,
        path="/",
    )
    response.set_cookie(
        key=settings.refresh_token_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        expires=refresh_expires_at,
        path="/",
    )


@router.get("/google/login")
async def google_login(request: Request):
    return await oauth.google_auth.authorize_redirect(
        request,
        settings.google_oauth_redirect_uri,
        access_type="offline",
        prompt="consent",
    )


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google_auth.authorize_access_token(request)

    # Authlib 1.x: userinfo is parsed automatically from the id_token
    profile = token.get("userinfo")
    if not profile:
        try:
            profile = await oauth.google_auth.userinfo(token=token)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google OAuth verification failed",
            ) from exc
    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google profile could not be read")

    user_repo = UserRepository(db)
    oauth_repo = OAuthRepository(db)

    email = profile["email"]
    user = user_repo.get_by_email(email)
    if user is None:
        user = user_repo.create(
            email=email,
            name=profile.get("name") or email,
            picture=profile.get("picture"),
        )
    else:
        user_repo.update_profile(user, name=profile.get("name") or email, picture=profile.get("picture"))

    expires_at = token.get("expires_at")
    token_expires_at = datetime.fromtimestamp(expires_at, tz=timezone.utc) if expires_at else None
    scopes = token.get("scope", "").split()

    oauth_repo.upsert_google_account(
        user_id=user.id,
        provider_account_id=str(profile.get("id") or profile.get("sub") or email),
        access_token=token.get("access_token"),
        refresh_token=token.get("refresh_token"),
        token_expires_at=token_expires_at,
        scopes=scopes,
    )

    db.commit()

    response = RedirectResponse(url=f"{settings.frontend_base_url}/dashboard")
    access_token, access_expires_at = create_access_token(str(user.id), {"email": user.email})
    refresh_token, refresh_expires_at = create_refresh_token(str(user.id), {"email": user.email})
    _set_auth_cookies(response, access_token, refresh_token, access_expires_at, refresh_expires_at)
    return response


@router.get("/session", response_model=AuthSessionResponse)
def get_session(user: User = Depends(get_current_user)):
    return AuthSessionResponse(
        user=UserRead(
            id=user.id,
            email=user.email,
            name=user.name,
            picture=user.picture,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_session(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get(settings.refresh_token_cookie_name)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    try:
        payload = decode_token(refresh_token, "refresh")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalid") from exc

    user_id = payload.get("sub")
    try:
        user_uuid = _uuid.UUID(user_id) if user_id else None
    except (ValueError, AttributeError):
        user_uuid = None
    if user_uuid is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh session")
    user = db.get(User, user_uuid)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access_token, access_expires_at = create_access_token(str(user.id), {"email": user.email})
    new_refresh_token, refresh_expires_at = create_refresh_token(str(user.id), {"email": user.email})
    _set_auth_cookies(response, access_token, new_refresh_token, access_expires_at, refresh_expires_at)
    db.commit()
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/logout")
def logout() -> Response:
    response = RedirectResponse(url=f"{settings.frontend_base_url}/login")
    response.delete_cookie(settings.access_token_cookie_name, path="/")
    response.delete_cookie(settings.refresh_token_cookie_name, path="/")
    return response
