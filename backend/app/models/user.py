from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.oauth_account import OAuthAccount
    from app.models.site import Site
    from app.models.storage_account import StorageAccount


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    picture: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sites: Mapped[list[Site]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    storage_accounts: Mapped[list[StorageAccount]] = relationship(back_populates="owner", cascade="all, delete-orphan")
