from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.models.hosted_archive import (
    HostedArchive,
    HostedArchiveBillingProvider,
    HostedArchiveBillingStatus,
    HostedArchiveLifecycle,
)
from app.services.storage_usage_service import ArchiveStorageUsage, compute_archive_storage_usage


@dataclass(frozen=True)
class PlanEntitlement:
    code: str
    label: str
    storage_quota_bytes: int | None
    monthly_price_display: str


PLAN_ENTITLEMENTS: dict[str, PlanEntitlement] = {
    "founding": PlanEntitlement(
        code="founding",
        label="Founding",
        storage_quota_bytes=25 * 1024 * 1024 * 1024,
        monthly_price_display="$9/mo",
    ),
    "family": PlanEntitlement(
        code="family",
        label="Family",
        storage_quota_bytes=75 * 1024 * 1024 * 1024,
        monthly_price_display="$19/mo",
    ),
    "family_plus": PlanEntitlement(
        code="family_plus",
        label="Family Plus",
        storage_quota_bytes=250 * 1024 * 1024 * 1024,
        monthly_price_display="$39/mo",
    ),
}


def hosted_archive_enabled(settings: Settings | None = None) -> bool:
    resolved = settings or get_settings()
    return resolved.hosted_archive_enabled


def normalize_lifecycle_state(lifecycle_state: str | HostedArchiveLifecycle) -> str:
    if isinstance(lifecycle_state, HostedArchiveLifecycle):
        return lifecycle_state.value
    normalized = lifecycle_state.strip()
    valid_states = {state.value for state in HostedArchiveLifecycle}
    if normalized not in valid_states:
        raise ValueError(
            "Unsupported hosted archive lifecycle state. "
            f"Expected one of: {', '.join(sorted(valid_states))}."
        )
    return normalized


def get_plan_entitlement(plan_code: str) -> PlanEntitlement:
    return PLAN_ENTITLEMENTS.get(plan_code, PLAN_ENTITLEMENTS["founding"])


async def get_hosted_archive(db: AsyncSession) -> HostedArchive | None:
    result = await db.execute(select(HostedArchive).limit(1))
    return result.scalar_one_or_none()


async def get_or_create_hosted_archive(
    db: AsyncSession,
    *,
    actor_id: str | None = None,
    settings: Settings | None = None,
) -> HostedArchive:
    archive = await get_hosted_archive(db)
    if archive:
        return archive

    resolved_settings = settings or get_settings()
    archive = HostedArchive(
        archive_key=resolved_settings.HOSTED_ARCHIVE_KEY.strip() or "hosted-archive",
        archive_name=resolved_settings.HOSTED_ARCHIVE_NAME.strip() or "Family Book Hosted Archive",
        owner_email=resolved_settings.HOSTED_ARCHIVE_OWNER_EMAIL.strip() or "owner@example.com",
        base_url=resolved_settings.BASE_URL.rstrip("/"),
        hosting_mode="managed_single_tenant",
        plan_code=resolved_settings.HOSTED_ARCHIVE_PLAN.strip() or "founding",
        lifecycle_state=HostedArchiveLifecycle.active.value,
        billing_provider=(
            HostedArchiveBillingProvider.stripe.value
            if resolved_settings.HOSTED_ARCHIVE_BILLING_PROVIDER.strip().lower() == "stripe"
            else HostedArchiveBillingProvider.manual.value
        ),
        billing_status=HostedArchiveBillingStatus.unconfigured.value,
        storage_quota_bytes=(
            resolved_settings.HOSTED_ARCHIVE_STORAGE_QUOTA_BYTES or
            get_plan_entitlement(resolved_settings.HOSTED_ARCHIVE_PLAN.strip() or "founding").storage_quota_bytes
        ),
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(archive)
    await db.flush()
    return archive


async def provision_hosted_archive(
    db: AsyncSession,
    *,
    actor_id: str | None,
    archive_name: str,
    owner_email: str,
    base_url: str,
    plan_code: str,
    support_notes: str | None = None,
) -> HostedArchive:
    settings = get_settings()
    archive = await get_hosted_archive(db)
    if archive is None:
        archive = HostedArchive(
            archive_key=base_url.replace("https://", "").replace("http://", "").replace("/", "-"),
            archive_name=archive_name,
            owner_email=owner_email,
            base_url=base_url.rstrip("/"),
            hosting_mode="managed_single_tenant",
            plan_code=plan_code,
            lifecycle_state=HostedArchiveLifecycle.active.value,
            billing_provider=(
                HostedArchiveBillingProvider.stripe.value
                if settings.HOSTED_ARCHIVE_BILLING_PROVIDER.strip().lower() == "stripe"
                else HostedArchiveBillingProvider.manual.value
            ),
            billing_status=HostedArchiveBillingStatus.unconfigured.value,
        )
        db.add(archive)
    else:
        archive.archive_name = archive_name
        archive.owner_email = owner_email
        archive.base_url = base_url.rstrip("/")
        archive.plan_code = plan_code

    entitlement = get_plan_entitlement(plan_code)
    archive.storage_quota_bytes = entitlement.storage_quota_bytes
    archive.lifecycle_state = HostedArchiveLifecycle.active.value
    archive.lifecycle_reason = None
    archive.support_notes = support_notes
    archive.updated_by = actor_id
    if archive.created_by is None:
        archive.created_by = actor_id
    await db.flush()
    return archive


async def set_archive_lifecycle_state(
    db: AsyncSession,
    *,
    archive: HostedArchive,
    lifecycle_state: str | HostedArchiveLifecycle,
    actor_id: str | None,
    reason: str | None = None,
    export_state: str | None = None,
    deletion_state: str | None = None,
) -> HostedArchive:
    archive.lifecycle_state = normalize_lifecycle_state(lifecycle_state)
    archive.lifecycle_reason = reason
    if export_state is not None:
        archive.export_state = export_state
    if deletion_state is not None:
        archive.deletion_state = deletion_state
    archive.updated_by = actor_id
    await db.flush()
    return archive


def archive_allows_writes(archive: HostedArchive | None) -> tuple[bool, str | None]:
    if archive is None:
        return True, None
    if archive.lifecycle_state == HostedArchiveLifecycle.suspended.value:
        return False, "Archive access is suspended."
    if archive.lifecycle_state in {
        HostedArchiveLifecycle.deletion_requested.value,
        HostedArchiveLifecycle.deleted.value,
    }:
        return False, "Archive is pending deletion."
    if archive.billing_status in {
        HostedArchiveBillingStatus.past_due.value,
        HostedArchiveBillingStatus.canceled.value,
        HostedArchiveBillingStatus.unpaid.value,
        HostedArchiveBillingStatus.suspended.value,
    }:
        return False, "Billing state blocks archive changes."
    return True, None


def archive_member_access_allowed(archive: HostedArchive | None) -> tuple[bool, int | None, str | None]:
    if archive is None:
        return False, 503, "Hosted archive is not provisioned."
    if archive.lifecycle_state == HostedArchiveLifecycle.suspended.value:
        return False, 423, "Archive access is suspended."
    if archive.lifecycle_state in {
        HostedArchiveLifecycle.deletion_requested.value,
        HostedArchiveLifecycle.deleted.value,
    }:
        return False, 423, "Archive is pending deletion."
    if archive.billing_status in {
        HostedArchiveBillingStatus.past_due.value,
        HostedArchiveBillingStatus.canceled.value,
        HostedArchiveBillingStatus.unpaid.value,
        HostedArchiveBillingStatus.suspended.value,
    }:
        return False, 402, "Hosted billing requires attention."
    return True, None, None


def archive_storage_quota_bytes(archive: HostedArchive | None) -> int | None:
    if archive is None:
        return None
    if archive.storage_quota_bytes is not None:
        return archive.storage_quota_bytes
    return get_plan_entitlement(archive.plan_code).storage_quota_bytes


def archive_usage_snapshot(archive: HostedArchive | None) -> dict[str, Any]:
    usage = compute_archive_storage_usage()
    quota_bytes = archive_storage_quota_bytes(archive)
    return {
        "usage": usage,
        "quota_bytes": quota_bytes,
        "quota_exceeded": quota_bytes is not None and usage.total_bytes > quota_bytes,
        "quota_remaining_bytes": (
            None if quota_bytes is None else max(quota_bytes - usage.total_bytes, 0)
        ),
    }


def build_operator_archive_summary(
    archive: HostedArchive,
    *,
    backup_health: dict[str, Any],
    usage: ArchiveStorageUsage,
) -> dict[str, Any]:
    entitlement = get_plan_entitlement(archive.plan_code)
    quota_bytes = archive_storage_quota_bytes(archive)
    return {
        "archive_key": archive.archive_key,
        "archive_name": archive.archive_name,
        "owner_email": archive.owner_email,
        "base_url": archive.base_url,
        "plan_code": archive.plan_code,
        "plan_label": entitlement.label,
        "monthly_price_display": entitlement.monthly_price_display,
        "lifecycle_state": archive.lifecycle_state,
        "lifecycle_reason": archive.lifecycle_reason,
        "billing_provider": archive.billing_provider,
        "billing_status": archive.billing_status,
        "stripe_customer_id": archive.stripe_customer_id,
        "stripe_subscription_id": archive.stripe_subscription_id,
        "trial_ends_at": archive.trial_ends_at,
        "current_period_end_at": archive.current_period_end_at,
        "storage_total_bytes": usage.total_bytes,
        "storage_quota_bytes": quota_bytes,
        "backup_fresh": backup_health.get("fresh"),
        "backup_latest_file": backup_health.get("latest_file"),
        "backup_retention_days": backup_health.get("retention_days"),
        "export_state": archive.export_state,
        "deletion_state": archive.deletion_state,
        "support_notes": archive.support_notes,
    }
