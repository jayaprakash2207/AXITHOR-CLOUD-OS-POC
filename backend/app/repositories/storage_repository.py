from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.storage_account import StorageAccount
from app.repositories.base import BaseRepository


class StorageRepository(BaseRepository):
    def get_by_user_and_provider(self, user_id: UUID, provider: str) -> StorageAccount | None:
        stmt = select(StorageAccount).where(
            StorageAccount.user_id == user_id,
            StorageAccount.provider == provider,
        )
        return self.db.scalar(stmt)

    def upsert_google_drive(
        self,
        *,
        user_id: UUID,
        access_token: str | None,
        refresh_token: str | None,
        quota: str | None,
        token_expires_at=None,
    ) -> StorageAccount:
        account = self.get_by_user_and_provider(user_id, "google_drive")
        if account is None:
            account = StorageAccount(user_id=user_id, provider="google_drive")
            self.db.add(account)

        account.access_token = access_token
        account.refresh_token = refresh_token
        account.token_expires_at = token_expires_at
        account.quota = quota
        self.db.flush()
        return account

    def delete(self, account: StorageAccount) -> None:
        self.db.delete(account)
        self.db.flush()