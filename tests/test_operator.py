import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.hosted_archive import HostedArchive


def _enable_hosted(monkeypatch):
    monkeypatch.setenv("HOSTED_ARCHIVE_ENABLED", "true")
    monkeypatch.setenv("HOSTED_ARCHIVE_BILLING_PROVIDER", "stripe")
    monkeypatch.setenv("OPERATOR_TOKENS", "operator-secret")


@pytest.mark.asyncio
async def test_operator_can_provision_suspend_and_reactivate_archive(
    client: AsyncClient,
    db: AsyncSession,
    monkeypatch,
):
    _enable_hosted(monkeypatch)
    headers = {"x-operator-token": "operator-secret"}

    provision_resp = await client.post(
        "/api/operator/archive/provision",
        headers=headers,
        json={
            "archive_name": "Cutroni Family",
            "owner_email": "owner@example.com",
            "base_url": "https://family.example.com",
            "plan_code": "family",
            "support_notes": "pilot",
        },
    )
    assert provision_resp.status_code == 200
    assert provision_resp.json()["archive_name"] == "Cutroni Family"
    assert provision_resp.json()["plan_code"] == "family"

    suspend_resp = await client.post(
        "/api/operator/archive/lifecycle",
        headers=headers,
        json={
            "lifecycle_state": "suspended",
            "reason": "billing hold",
            "export_state": "ready",
            "deletion_state": "none",
        },
    )
    assert suspend_resp.status_code == 200
    assert suspend_resp.json()["lifecycle_state"] == "suspended"
    assert suspend_resp.json()["lifecycle_reason"] == "billing hold"

    reactivate_resp = await client.post(
        "/api/operator/archive/lifecycle",
        headers=headers,
        json={"lifecycle_state": "active"},
    )
    assert reactivate_resp.status_code == 200
    assert reactivate_resp.json()["lifecycle_state"] == "active"

    archive = (await db.execute(select(HostedArchive))).scalar_one()
    assert archive.owner_email == "owner@example.com"
    assert archive.lifecycle_state == "active"

    audit_rows = (
        await db.execute(select(AuditLog).where(AuditLog.entity_type == "hosted_archive"))
    ).scalars().all()
    assert len(audit_rows) >= 3


@pytest.mark.asyncio
async def test_operator_rejects_unknown_lifecycle_state(
    client: AsyncClient,
    db: AsyncSession,
    monkeypatch,
):
    _enable_hosted(monkeypatch)
    headers = {"x-operator-token": "operator-secret"}

    await client.post(
        "/api/operator/archive/provision",
        headers=headers,
        json={
            "archive_name": "Cutroni Family",
            "owner_email": "owner@example.com",
            "base_url": "https://family.example.com",
            "plan_code": "family",
        },
    )

    invalid_resp = await client.post(
        "/api/operator/archive/lifecycle",
        headers=headers,
        json={"lifecycle_state": "suspendd", "reason": "typo"},
    )

    assert invalid_resp.status_code == 422
    assert "Unsupported hosted archive lifecycle state" in invalid_resp.json()["detail"]

    archive = (await db.execute(select(HostedArchive))).scalar_one()
    assert archive.lifecycle_state == "active"
    assert archive.lifecycle_reason is None


@pytest.mark.asyncio
async def test_operator_console_page_renders_safe_summary(
    client: AsyncClient,
    monkeypatch,
):
    _enable_hosted(monkeypatch)
    resp = await client.get("/operator?token=operator-secret")

    assert resp.status_code == 200
    assert "Operator Console" in resp.text
    assert "Hosted archive support view" in resp.text
    assert "Pending accounts" in resp.text


@pytest.mark.asyncio
async def test_suspended_hosted_archive_blocks_member_access_but_allows_admin_settings(
    admin_client: AsyncClient,
    member_client: AsyncClient,
    db: AsyncSession,
    monkeypatch,
):
    _enable_hosted(monkeypatch)
    db.add(
        HostedArchive(
            archive_key="archive-1",
            archive_name="Hosted Archive",
            owner_email="owner@example.com",
            base_url="https://family.example.com",
            hosting_mode="managed_single_tenant",
            plan_code="founding",
            lifecycle_state="suspended",
            billing_provider="stripe",
            billing_status="active",
        )
    )
    await db.commit()

    member_resp = await member_client.get("/tree")
    admin_resp = await admin_client.get("/settings")

    assert member_resp.status_code == 423
    assert admin_resp.status_code == 200


@pytest.mark.asyncio
async def test_missing_hosted_archive_record_fails_closed_for_app_access(
    admin_client: AsyncClient,
    member_client: AsyncClient,
    monkeypatch,
):
    _enable_hosted(monkeypatch)

    member_resp = await member_client.get("/tree")
    admin_resp = await admin_client.get("/settings")

    assert member_resp.status_code == 503
    assert member_resp.json()["detail"] == "Hosted archive is not provisioned."
    assert admin_resp.status_code == 503
    assert admin_resp.json()["detail"] == "Hosted archive is not provisioned."
