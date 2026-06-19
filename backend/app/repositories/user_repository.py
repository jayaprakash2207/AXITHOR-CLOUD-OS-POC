from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.db.get(User, user_id)

    def create(self, *, email: str, name: str, picture: str | None) -> User:
        user = User(email=email, name=name, picture=picture)
        self.db.add(user)
        self.db.flush()
        return user

    def update_profile(self, user: User, *, name: str, picture: str | None) -> User:
        user.name = name
        user.picture = picture
        self.db.flush()
        return user
