from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.deployment import Deployment
    from app.models.domain import Domain
    from app.models.file_metadata import FileMetadata
    from app.models.user import User
    from app.models.website_file import WebsiteFile


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subdomain: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)
    drive_folder_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    custom_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    owner: Mapped[User] = relationship(back_populates="sites")
    deployments: Mapped[list[Deployment]] = relationship(back_populates="site", cascade="all, delete-orphan")
    files: Mapped[list[WebsiteFile]] = relationship(back_populates="site", cascade="all, delete-orphan")
    domains: Mapped[list[Domain]] = relationship(back_populates="site", cascade="all, delete-orphan")
    file_metadata: Mapped[list[FileMetadata]] = relationship(back_populates="site", cascade="all, delete-orphan")
