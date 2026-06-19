"""modules 3-7: deployment engine, subdomain routing, metadata, sync, cache

Revision ID: 0003_modules_3_7
Revises: 0002_storage_accounts
Create Date: 2026-06-18
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_modules_3_7"
down_revision = "0002_storage_accounts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "website_files",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "site_id",
            sa.Uuid(),
            sa.ForeignKey("sites.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("path", sa.String(length=1024), nullable=False),
        sa.Column("provider_file_id", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=128), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )

    op.create_table(
        "domains",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "site_id",
            sa.Uuid(),
            sa.ForeignKey("sites.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("domain", sa.String(length=255), unique=True, nullable=False),
        sa.Column("ssl_status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )

    op.create_table(
        "file_metadata",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "site_id",
            sa.Uuid(),
            sa.ForeignKey("sites.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("path", sa.String(length=1024), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False, server_default="google_drive"),
        sa.Column("provider_file_id", sa.String(length=255), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint(
            "site_id", "path", "version", name="uq_file_metadata_site_path_version"
        ),
    )

    op.create_table(
        "sync_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "site_id",
            sa.Uuid(),
            sa.ForeignKey("sites.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("provider_resource_id", sa.String(length=255), nullable=True),
        sa.Column("payload", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("sync_events")
    op.drop_table("file_metadata")
    op.drop_table("domains")
    op.drop_table("website_files")
