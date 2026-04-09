import hashlib
import hmac
import json
import time

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hosted_archive import BillingEventReceipt, HostedArchive


def _enable_hosted_billing(monkeypatch):
    monkeypatch.setenv("HOSTED_ARCHIVE_ENABLED", "true")
    monkeypatch.setenv("HOSTED_ARCHIVE_BILLING_PROVIDER", "stripe")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_123")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_123")
    monkeypatch.setenv("STRIPE_PRICE_FOUNDING", "price_founding")


def _sign_payload(payload: bytes, secret: str) -> str:
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
    digest = hmac.new(secret.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


@pytest.mark.asyncio
async def test_billing_checkout_is_disabled_for_self_hosted(admin_client: AsyncClient):
    resp = await admin_client.post("/api/billing/checkout", json={"plan_code": "founding"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_admin_can_start_hosted_checkout(
    admin_client: AsyncClient,
    db: AsyncSession,
    monkeypatch,
):
    _enable_hosted_billing(monkeypatch)
    archive = HostedArchive(
        archive_key="archive-1",
        archive_name="Hosted Archive",
        owner_email="owner@example.com",
        base_url="https://family.example.com",
        hosting_mode="managed_single_tenant",
        plan_code="founding",
        lifecycle_state="active",
        billing_provider="stripe",
        billing_status="unconfigured",
        created_by="tyler-000-0000-0000-000000000002",
    )
    db.add(archive)
    await db.commit()

    async def fake_post_to_stripe(settings, endpoint, payload):
        assert endpoint == "checkout/sessions"
        assert payload["metadata[archive_key]"] == "archive-1"
        return {"id": "cs_test_123", "url": "https://checkout.stripe.com/pay/cs_test_123"}

    monkeypatch.setattr("app.services.billing_service._post_to_stripe", fake_post_to_stripe)

    resp = await admin_client.post("/api/billing/checkout", json={"plan_code": "founding"})

    assert resp.status_code == 200
    assert resp.json()["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_123"
    assert resp.json()["session_id"] == "cs_test_123"


@pytest.mark.asyncio
async def test_stripe_webhook_updates_subscription_state_idempotently(
    client: AsyncClient,
    db: AsyncSession,
    monkeypatch,
):
    _enable_hosted_billing(monkeypatch)
    archive = HostedArchive(
        archive_key="archive-1",
        archive_name="Hosted Archive",
        owner_email="owner@example.com",
        base_url="https://family.example.com",
        hosting_mode="managed_single_tenant",
        plan_code="founding",
        lifecycle_state="active",
        billing_provider="stripe",
        billing_status="unconfigured",
    )
    db.add(archive)
    await db.commit()

    event = {
        "id": "evt_123",
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_123",
                "customer": "cus_123",
                "status": "past_due",
                "current_period_end": 1_800_000_000,
                "trial_end": None,
                "metadata": {
                    "archive_key": "archive-1",
                    "plan_code": "founding",
                },
                "items": {"data": [{"price": {"id": "price_founding"}}]},
            }
        },
    }
    payload = json.dumps(event).encode("utf-8")
    signature = _sign_payload(payload, "whsec_test_123")

    resp1 = await client.post(
        "/api/billing/stripe/webhook",
        headers={"stripe-signature": signature},
        content=payload,
    )
    resp2 = await client.post(
        "/api/billing/stripe/webhook",
        headers={"stripe-signature": signature},
        content=payload,
    )

    assert resp1.status_code == 200
    assert resp2.status_code == 200

    await db.refresh(archive)
    refreshed = (await db.execute(select(HostedArchive))).scalar_one()
    assert refreshed.billing_status == "past_due"
    assert refreshed.stripe_customer_id == "cus_123"
    assert refreshed.stripe_subscription_id == "sub_123"

    receipts = (await db.execute(select(BillingEventReceipt))).scalars().all()
    assert len(receipts) == 1
