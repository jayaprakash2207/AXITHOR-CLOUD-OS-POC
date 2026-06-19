"""make site.drive_folder_id optional

Revision ID: 0004_site_drive_folder_optional
Revises: 0003_modules_3_7
Create Date: 2026-06-19
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004_site_drive_folder_optional"
down_revision = "0003_modules_3_7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("sites") as batch_op:
        batch_op.alter_column(
            "drive_folder_id",
            existing_type=sa.String(255),
            nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("sites") as batch_op:
        batch_op.alter_column(
            "drive_folder_id",
            existing_type=sa.String(255),
            nullable=False,
        )
