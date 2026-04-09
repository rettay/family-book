from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.models.hosted_archive import BillingEventReceipt, HostedArchive
from app.services.hosted_archive_service import get_plan_entitlement


class BillingConfigurationError(ValueError):
    pass


class StripeWebhookError(ValueError):
    pass


@dataclass(frozen=True)
class CheckoutSessionResult:
    session_id: str
    checkout_url: str


def _stripe_headers(settings: Settings) -> dict[str, str]:
    if not settings.stripe_secret_key_value:
        raise BillingConfigurationError("Stripe secret key is not configured.")
    return {
        "Authorization": f"Bearer {settings.stripe_secret_key_value}",
        "Content-Type": "application/x-www-form-urlencoded",
    }


async def _post_to_stripe(settings: Settings, endpoint: str, payload: dict[str, str]) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"https://api.stripe.com/v1/{endpoint}",
            headers=_stripe_headers(settings),
            content=urlencode(payload),
        )
    response.raise_for_status()
    return response.json()


async def create_checkout_session(
    archive: HostedArchive,
    *,
    plan_code: str,
    settings: Settings | None = None,
) -> CheckoutSessionResult:
    resolved_settings = settings or get_settings()
    if not resolved_settings.hosted_archive_enabled:
        raise BillingConfigurationError("Hosted billing is not enabled.")
    price_id = resolved_settings.stripe_price_map.get(plan_code)
    if not price_id:
        raise BillingConfigurationError(f"No Stripe price is configured for plan {plan_code}.")

    payload = {
        "mode": "subscription",
        "success_url": f"{resolved_settings.BASE_URL.rstrip('/')}/settings?billing=success",
        "cancel_url": f"{resolved_settings.BASE_URL.rstrip('/')}/settings?billing=cancelled",
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": "1",
        "client_reference_id": archive.archive_key,
        "metadata[archive_key]": archive.archive_key,
        "metadata[plan_code]": plan_code,
        "subscription_data[metadata][archive_key]": archive.archive_key,
        "subscription_data[metadata][plan_code]": plan_code,
        "customer_email": archive.owner_email,
    }
    stripe_response = await _post_to_stripe(resolved_settings, "checkout/sessions", payload)
    return CheckoutSessionResult(
        session_id=stripe_response["id"],
        checkout_url=stripe_response["url"],
    )


async def create_billing_portal_session(
    archive: HostedArchive,
    *,
    settings: Settings | None = None,
) -> str:
    resolved_settings = settings or get_settings()
    if not archive.stripe_customer_id:
        raise BillingConfigurationError("Archive has no Stripe customer id.")
    payload = {
        "customer": archive.stripe_customer_id,
        "return_url": f"{resolved_settings.BASE_URL.rstrip('/')}/settings",
    }
    stripe_response = await _post_to_stripe(resolved_settings, "billing_portal/sessions", payload)
    return stripe_response["url"]


def _parse_stripe_signature_header(signature_header: str) -> tuple[int, list[str]]:
    timestamp = None
    signatures: list[str] = []
    for segment in signature_header.split(","):
        key, _, value = segment.partition("=")
        if key == "t":
            timestamp = int(value)
        elif key == "v1":
            signatures.append(value)
    if timestamp is None or not signatures:
        raise StripeWebhookError("Invalid Stripe signature header.")
    return timestamp, signatures


def verify_stripe_webhook_signature(
    payload: bytes,
    signature_header: str,
    *,
    settings: Settings | None = None,
    tolerance_seconds: int = 300,
) -> dict:
    resolved_settings = settings or get_settings()
    secret = resolved_settings.stripe_webhook_secret_value
    if not secret:
        raise StripeWebhookError("Stripe webhook secret is not configured.")
    timestamp, signatures = _parse_stripe_signature_header(signature_header)
    if abs(time.time() - timestamp) > tolerance_seconds:
        raise StripeWebhookError("Stripe webhook timestamp is too old.")
    signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
    expected = hmac.new(secret.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(expected, signature) for signature in signatures):
        raise StripeWebhookError("Stripe webhook signature mismatch.")
    return json.loads(payload)


def _iso_or_none(value: int | str | None) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, str):
        return value
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()


async def apply_stripe_event(
    db: AsyncSession,
    event: dict,
) -> HostedArchive | None:
    event_id = event.get("id")
    event_type = event.get("type", "")
    if not event_id:
        raise StripeWebhookError("Stripe event id is missing.")

    existing = await db.execute(
        select(BillingEventReceipt).where(BillingEventReceipt.external_event_id == event_id)
    )
    if existing.scalar_one_or_none():
        archive = await _archive_for_stripe_event(db, event)
        return archive

    archive = await _archive_for_stripe_event(db, event)
    archive_key = archive.archive_key if archive else None
    receipt = BillingEventReceipt(
        provider="stripe",
        external_event_id=event_id,
        event_type=event_type,
        archive_key=archive_key,
        processing_status="processed",
        summary_json=json.dumps(
            {
                "type": event_type,
                "archive_key": archive_key,
            }
        ),
    )
    db.add(receipt)

    if archive:
        _apply_archive_billing_update(archive, event)
        await db.flush()
    else:
        await db.flush()

    return archive


async def _archive_for_stripe_event(db: AsyncSession, event: dict) -> HostedArchive | None:
    data_object = event.get("data", {}).get("object", {})
    metadata = data_object.get("metadata", {}) or {}
    archive_key = metadata.get("archive_key")

    if archive_key:
        result = await db.execute(select(HostedArchive).where(HostedArchive.archive_key == archive_key))
        archive = result.scalar_one_or_none()
        if archive:
            return archive

    customer_id = data_object.get("customer")
    subscription_id = data_object.get("subscription") or data_object.get("id")
    if customer_id:
        result = await db.execute(
            select(HostedArchive).where(HostedArchive.stripe_customer_id == customer_id)
        )
        archive = result.scalar_one_or_none()
        if archive:
            return archive
    if subscription_id and event.get("type", "").startswith("customer.subscription"):
        result = await db.execute(
            select(HostedArchive).where(HostedArchive.stripe_subscription_id == subscription_id)
        )
        return result.scalar_one_or_none()
    return None


def _apply_archive_billing_update(archive: HostedArchive, event: dict) -> None:
    event_type = event.get("type", "")
    data_object = event.get("data", {}).get("object", {})
    metadata = data_object.get("metadata", {}) or {}
    plan_code = metadata.get("plan_code")
    if plan_code:
        archive.plan_code = plan_code
        archive.storage_quota_bytes = get_plan_entitlement(plan_code).storage_quota_bytes

    if event_type == "checkout.session.completed":
        archive.billing_status = "active"
        archive.stripe_customer_id = data_object.get("customer") or archive.stripe_customer_id
        archive.stripe_subscription_id = (
            data_object.get("subscription") or archive.stripe_subscription_id
        )
        archive.stripe_price_id = data_object.get("metadata", {}).get("price_id") or archive.stripe_price_id
        archive.current_period_end_at = _iso_or_none(data_object.get("expires_at"))
        return

    if event_type.startswith("customer.subscription"):
        archive.stripe_customer_id = data_object.get("customer") or archive.stripe_customer_id
        archive.stripe_subscription_id = data_object.get("id") or archive.stripe_subscription_id
        archive.billing_status = data_object.get("status") or archive.billing_status
        archive.current_period_end_at = _iso_or_none(data_object.get("current_period_end"))
        archive.trial_ends_at = _iso_or_none(data_object.get("trial_end"))
        items = data_object.get("items", {}).get("data", [])
        if items:
            archive.stripe_price_id = items[0].get("price", {}).get("id") or archive.stripe_price_id
        return

    if event_type == "invoice.payment_failed":
        archive.billing_status = "past_due"
        archive.stripe_customer_id = data_object.get("customer") or archive.stripe_customer_id
        return

    if event_type == "invoice.paid":
        archive.billing_status = "active"
        archive.stripe_customer_id = data_object.get("customer") or archive.stripe_customer_id
