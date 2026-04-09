import enum

from sqlalchemy import BigInteger, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, generate_uuid


class HostedArchiveLifecycle(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    deletion_requested = "deletion_requested"
    deleted = "deleted"


class HostedArchiveBillingStatus(str, enum.Enum):
    unconfigured = "unconfigured"
    trialing = "trialing"
    active = "active"
    past_due = "past_due"
    canceled = "canceled"
    unpaid = "unpaid"
    suspended = "suspended"


class HostedArchiveBillingProvider(str, enum.Enum):
    none = "none"
    stripe = "stripe"
    manual = "manual"


class HostedArchive(Base, TimestampMixin):
    __tablename__ = "hosted_archives"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    archive_key: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    archive_name: Mapped[str] = mapped_column(String(200))
    owner_email: Mapped[str] = mapped_column(String(320))
    base_url: Mapped[str] = mapped_column(String(500))
    hosting_mode: Mapped[str] = mapped_column(String(40), default="managed_single_tenant")
    plan_code: Mapped[str] = mapped_column(String(40), default="founding")
    lifecycle_state: Mapped[str] = mapped_column(
        String(40), default=HostedArchiveLifecycle.active.value
    )
    lifecycle_reason: Mapped[str | None] = mapped_column(Text, default=None)
    billing_provider: Mapped[str] = mapped_column(
        String(20), default=HostedArchiveBillingProvider.none.value
    )
    billing_status: Mapped[str] = mapped_column(
        String(20), default=HostedArchiveBillingStatus.unconfigured.value
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(100), default=None)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(100), default=None)
    stripe_price_id: Mapped[str | None] = mapped_column(String(100), default=None)
    trial_ends_at: Mapped[str | None] = mapped_column(String(40), default=None)
    current_period_end_at: Mapped[str | None] = mapped_column(String(40), default=None)
    storage_quota_bytes: Mapped[int | None] = mapped_column(BigInteger, default=None)
    export_state: Mapped[str] = mapped_column(String(30), default="none")
    deletion_state: Mapped[str] = mapped_column(String(30), default="none")
    support_notes: Mapped[str | None] = mapped_column(Text, default=None)
    created_by: Mapped[str | None] = mapped_column(String(36), default=None)
    updated_by: Mapped[str | None] = mapped_column(String(36), default=None)


class BillingEventReceipt(Base, TimestampMixin):
    __tablename__ = "billing_event_receipts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    provider: Mapped[str] = mapped_column(String(20))
    external_event_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(100))
    archive_key: Mapped[str | None] = mapped_column(String(80), default=None)
    processing_status: Mapped[str] = mapped_column(String(20), default="processed")
    summary_json: Mapped[str | None] = mapped_column(Text, default=None)

    __table_args__ = (
        Index("idx_billing_receipts_provider_status", "provider", "processing_status"),
    )
