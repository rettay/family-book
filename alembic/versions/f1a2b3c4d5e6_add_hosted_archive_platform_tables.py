"""add hosted archive platform tables

Revision ID: f1a2b3c4d5e6
Revises: c4f8e2a1b6d9
Create Date: 2026-04-08 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "c4f8e2a1b6d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "hosted_archives",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("archive_key", sa.String(length=80), nullable=False),
        sa.Column("archive_name", sa.String(length=200), nullable=False),
        sa.Column("owner_email", sa.String(length=320), nullable=False),
        sa.Column("base_url", sa.String(length=500), nullable=False),
        sa.Column("hosting_mode", sa.String(length=40), nullable=False),
        sa.Column("plan_code", sa.String(length=40), nullable=False),
        sa.Column("lifecycle_state", sa.String(length=40), nullable=False),
        sa.Column("lifecycle_reason", sa.Text(), nullable=True),
        sa.Column("billing_provider", sa.String(length=20), nullable=False),
        sa.Column("billing_status", sa.String(length=20), nullable=False),
        sa.Column("stripe_customer_id", sa.String(length=100), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(length=100), nullable=True),
        sa.Column("stripe_price_id", sa.String(length=100), nullable=True),
        sa.Column("trial_ends_at", sa.String(length=40), nullable=True),
        sa.Column("current_period_end_at", sa.String(length=40), nullable=True),
        sa.Column("storage_quota_bytes", sa.BigInteger(), nullable=True),
        sa.Column("export_state", sa.String(length=30), nullable=False),
        sa.Column("deletion_state", sa.String(length=30), nullable=False),
        sa.Column("support_notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("updated_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("archive_key"),
    )
    op.create_index(
        op.f("ix_hosted_archives_archive_key"),
        "hosted_archives",
        ["archive_key"],
        unique=True,
    )

    op.create_table(
        "billing_event_receipts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("external_event_id", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("archive_key", sa.String(length=80), nullable=True),
        sa.Column("processing_status", sa.String(length=20), nullable=False),
        sa.Column("summary_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_event_id"),
    )
    op.create_index(
        op.f("ix_billing_event_receipts_external_event_id"),
        "billing_event_receipts",
        ["external_event_id"],
        unique=True,
    )
    op.create_index(
        "idx_billing_receipts_provider_status",
        "billing_event_receipts",
        ["provider", "processing_status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_billing_receipts_provider_status", table_name="billing_event_receipts")
    op.drop_index(
        op.f("ix_billing_event_receipts_external_event_id"),
        table_name="billing_event_receipts",
    )
    op.drop_table("billing_event_receipts")
    op.drop_index(op.f("ix_hosted_archives_archive_key"), table_name="hosted_archives")
    op.drop_table("hosted_archives")
