from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import settings


class GoogleDriveStorageService:
    token_url = "https://oauth2.googleapis.com/token"
    metadata_url = "https://www.googleapis.com/drive/v3/about"

    def __init__(self, access_token: str | None, refresh_token: str | None) -> None:
        self.access_token = access_token
        self.refresh_token = refresh_token

    async def refresh_access_token(self) -> tuple[str, str | None, datetime | None]:
        if not self.refresh_token:
            raise ValueError("Refresh token missing")

        payload = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(self.token_url, data=payload)
            response.raise_for_status()
            token = response.json()

        access_token = token["access_token"]
        refresh_token = token.get("refresh_token", self.refresh_token)
        expires_in = token.get("expires_in")
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in)) if expires_in else None
        self.access_token = access_token
        self.refresh_token = refresh_token
        return access_token, refresh_token, expires_at

    async def _ensure_access_token(self) -> str:
        if self.access_token:
            return self.access_token
        access_token, _, _ = await self.refresh_access_token()
        return access_token

    async def _request_about(self, token: str) -> dict[str, object]:
        headers = {"Authorization": f"Bearer {token}"}
        params = {"fields": "storageQuota,user(displayName,emailAddress),rootFolderId"}
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(self.metadata_url, params=params, headers=headers)
            if response.status_code == 401:
                raise PermissionError("Access token expired")
            response.raise_for_status()
            return response.json()

    async def get_quota_and_metadata(self) -> tuple[dict[str, int | str | None], dict[str, str | int | None]]:
        token = await self._ensure_access_token()
        try:
            payload = await self._request_about(token)
        except PermissionError:
            access_token, refresh_token, _ = await self.refresh_access_token()
            self.access_token = access_token
            if refresh_token:
                self.refresh_token = refresh_token
            payload = await self._request_about(access_token)

        storage_quota = payload.get("storageQuota", {})
        drive_metadata = {
            "displayName": payload.get("user", {}).get("displayName"),
            "emailAddress": payload.get("user", {}).get("emailAddress"),
            "rootFolderId": payload.get("rootFolderId"),
        }
        return storage_quota, drive_metadata

    async def disconnect(self) -> None:
        if not self.access_token:
            return
        async with httpx.AsyncClient(timeout=20.0) as client:
            await client.post("https://oauth2.googleapis.com/revoke", params={"token": self.access_token})