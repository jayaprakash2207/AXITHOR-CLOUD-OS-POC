"""add token_expires_at to storage_accounts

Revision ID: 0005_storage_token_expires_at
Revises: 0004_site_drive_folder_optional
Create Date: 2026-06-19
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005_storage_token_expires_at"
down_revision = "0004_site_drive_folder_optional"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("storage_accounts") as batch_op:
        batch_op.add_column(
            sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("storage_accounts") as batch_op:
        batch_op.drop_column("token_expires_at")
