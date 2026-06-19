from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from app.models.oauth_account import OAuthAccount
from app.repositories.base import BaseRepository


class OAuthRepository(BaseRepository):
    def get_by_provider_account(self, provider: str, provider_account_id: str) -> OAuthAccount | None:
        stmt = select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_account_id == provider_account_id,
        )
        return self.db.scalar(stmt)

    def get_by_user_id(self, user_id: UUID, provider: str) -> OAuthAccount | None:
        stmt = select(OAuthAccount).where(OAuthAccount.user_id == user_id, OAuthAccount.provider == provider)
        return self.db.scalar(stmt)

    def get_google_account(self, user_id: UUID) -> OAuthAccount | None:
        return self.get_by_user_id(user_id, "google")

    def upsert_google_account(
        self,
        *,
        user_id: UUID,
        provider_account_id: str,
        access_token: str | None,
        refresh_token: str | None,
        token_expires_at: datetime | None,
        scopes: list[str] | None,
    ) -> OAuthAccount:
        account = self.get_by_provider_account("google", provider_account_id)
        if account is None:
            account = OAuthAccount(
                user_id=user_id,
                provider="google",
                provider_account_id=provider_account_id,
            )
            self.db.add(account)

        account.access_token = access_token
        account.refresh_token = refresh_token
        account.token_expires_at = token_expires_at
        account.scopes = " ".join(scopes) if scopes else None
        self.db.flush()
        return account
