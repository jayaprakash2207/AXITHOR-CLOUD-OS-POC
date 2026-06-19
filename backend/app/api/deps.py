import uuid as _uuid

from fastapi import Depends, HTTPException, Request, Response, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository


def _set_access_cookie(response: Response, token: str, expires_at) -> None:
    response.set_cookie(
        key=settings.access_token_cookie_name,
        value=token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        expires=expires_at,
        path="/",
    )


def get_current_user(request: Request, response: Response, db: Session = Depends(get_db)) -> User:
    access_token = request.cookies.get(settings.access_token_cookie_name)
    refresh_token = request.cookies.get(settings.refresh_token_cookie_name)
    user_repo = UserRepository(db)

    def _parse_uuid(val: str | None) -> _uuid.UUID | None:
        try:
            return _uuid.UUID(val) if val else None
        except (ValueError, AttributeError):
            return None

    if access_token:
        try:
            payload = decode_token(access_token, "access")
            user_id = _parse_uuid(payload.get("sub"))
        except JWTError:
            user_id = None
        if user_id:
            user = user_repo.get_by_id(user_id)
            if user is not None:
                return user

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    try:
        payload = decode_token(refresh_token, "refresh")
        user_id = _parse_uuid(payload.get("sub"))
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh session",
        ) from exc

    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh session")

    user = user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token, access_expires_at = create_access_token(str(user.id), {"email": user.email})
    _set_access_cookie(response, access_token, access_expires_at)
    return user
