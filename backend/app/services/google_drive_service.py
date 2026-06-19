from __future__ import annotations

import io
from dataclasses import dataclass

import httpx


@dataclass(slots=True)
class GoogleDriveFolder:
    id: str
    name: str


_DRIVE_UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files"
_DRIVE_FILES_URL = "https://www.googleapis.com/drive/v3/files"
_DRIVE_CHANNELS_URL = "https://www.googleapis.com/drive/v3/channels/stop"
_DRIVE_WATCH_URL = "https://www.googleapis.com/drive/v3/files/watch"


class GoogleDriveService:
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}

    # ------------------------------------------------------------------ #
    # List                                                                 #
    # ------------------------------------------------------------------ #

    async def list_site_files(self, folder_id: str) -> list[dict[str, str]]:
        params = {
            "q": f"'{folder_id}' in parents and trashed = false",
            "fields": "files(id,name,mimeType,modifiedTime,size)",
            "pageSize": 1000,
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(_DRIVE_FILES_URL, params=params, headers=self._headers)
            response.raise_for_status()
            return response.json().get("files", [])

    # ------------------------------------------------------------------ #
    # Upload                                                               #
    # ------------------------------------------------------------------ #

    async def upload_file(
        self,
        folder_id: str,
        filename: str,
        content: bytes,
        mime_type: str = "application/octet-stream",
    ) -> str:
        """Upload a file to a Drive folder and return the file ID."""
        metadata = {"name": filename, "parents": [folder_id]}

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Check if a file with the same name already exists
            existing_id = await self._find_file_in_folder(client, folder_id, filename)

            if existing_id:
                # Update existing file content
                response = await client.patch(
                    f"{_DRIVE_UPLOAD_URL}/{existing_id}",
                    params={"uploadType": "media"},
                    headers={**self._headers, "Content-Type": mime_type},
                    content=content,
                )
                response.raise_for_status()
                return existing_id

            # Multipart upload for new file
            boundary = "axithor_boundary"
            body = (
                f"--{boundary}\r\n"
                f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
                f'{{"name": "{filename}", "parents": ["{folder_id}"]}}\r\n'
                f"--{boundary}\r\n"
                f"Content-Type: {mime_type}\r\n\r\n"
            ).encode() + content + f"\r\n--{boundary}--".encode()

            response = await client.post(
                _DRIVE_UPLOAD_URL,
                params={"uploadType": "multipart"},
                headers={
                    **self._headers,
                    "Content-Type": f"multipart/related; boundary={boundary}",
                },
                content=body,
            )
            response.raise_for_status()
            return response.json()["id"]

    async def _find_file_in_folder(
        self, client: httpx.AsyncClient, folder_id: str, filename: str
    ) -> str | None:
        params = {
            "q": f"'{folder_id}' in parents and name = '{filename}' and trashed = false",
            "fields": "files(id)",
        }
        response = await client.get(_DRIVE_FILES_URL, params=params, headers=self._headers)
        if response.is_error:
            return None
        files = response.json().get("files", [])
        return files[0]["id"] if files else None

    # ------------------------------------------------------------------ #
    # Create folder                                                        #
    # ------------------------------------------------------------------ #

    async def create_folder(self, name: str, parent_id: str | None = None) -> GoogleDriveFolder:
        metadata: dict = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            metadata["parents"] = [parent_id]
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                _DRIVE_FILES_URL,
                headers={**self._headers, "Content-Type": "application/json"},
                json=metadata,
            )
            response.raise_for_status()
            data = response.json()
            return GoogleDriveFolder(id=data["id"], name=data["name"])

    # ------------------------------------------------------------------ #
    # Download                                                             #
    # ------------------------------------------------------------------ #

    async def download_file(self, file_id: str) -> bytes:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{_DRIVE_FILES_URL}/{file_id}",
                params={"alt": "media"},
                headers=self._headers,
            )
            response.raise_for_status()
            return response.content

    async def get_file_metadata(self, file_id: str) -> dict:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{_DRIVE_FILES_URL}/{file_id}",
                params={"fields": "id,name,mimeType,size,modifiedTime"},
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()

    # ------------------------------------------------------------------ #
    # Delete                                                               #
    # ------------------------------------------------------------------ #

    async def delete_file(self, file_id: str) -> None:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.delete(
                f"{_DRIVE_FILES_URL}/{file_id}",
                headers=self._headers,
            )
            response.raise_for_status()

    # ------------------------------------------------------------------ #
    # Watch (webhooks for Module 6)                                        #
    # ------------------------------------------------------------------ #

    async def watch_folder(
        self,
        folder_id: str,
        channel_id: str,
        webhook_url: str,
        token: str | None = None,
    ) -> dict:
        body: dict = {
            "id": channel_id,
            "type": "web_hook",
            "address": webhook_url,
        }
        if token:
            body["token"] = token
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{_DRIVE_FILES_URL}/{folder_id}/watch",
                headers={**self._headers, "Content-Type": "application/json"},
                json=body,
            )
            response.raise_for_status()
            return response.json()

    async def stop_watch(self, channel_id: str, resource_id: str) -> None:
        body = {"id": channel_id, "resourceId": resource_id}
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                _DRIVE_CHANNELS_URL,
                headers={**self._headers, "Content-Type": "application/json"},
                json=body,
            )
            # 204 No Content on success; 404 if already stopped
            if response.status_code not in (204, 404):
                response.raise_for_status()
