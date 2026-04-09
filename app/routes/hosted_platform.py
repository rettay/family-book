from __future__ import annotations

import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin
from app.backup.service import get_backup_health
from app.config import get_settings
from app.database import get_db
from app.i18n import translate
from app.models.auth import UserSession
from app.models.media import Media
from app.models.person import AccountState, Person
from app.services.audit_service import log_audit
from app.services.billing_service import (
    BillingConfigurationError,
    StripeWebhookError,
    apply_stripe_event,
    create_billing_portal_session,
    create_checkout_session,
    verify_stripe_webhook_signature,
)
from app.services.hosted_archive_service import (
    archive_usage_snapshot,
    build_operator_archive_summary,
    get_hosted_archive,
    get_or_create_hosted_archive,
    get_plan_entitlement,
    hosted_archive_enabled,
    provision_hosted_archive,
    set_archive_lifecycle_state,
)
from app.services.storage_usage_service import compute_archive_storage_usage, format_bytes
from app.services.theme_service import get_runtime_theme_from_app


logger = logging.getLogger(__name__)
router = APIRouter(tags=["hosted-platform"])
_template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=_template_dir)


class HostedArchiveProvisionRequest(BaseModel):
    archive_name: str
    owner_email: str
    base_url: str
    plan_code: str
    support_notes: str | None = None


class HostedArchiveLifecycleRequest(BaseModel):
    lifecycle_state: str
    reason: str | None = None
    export_state: str | None = None
    deletion_state: str | None = None


class BillingCheckoutRequest(BaseModel):
    plan_code: str


def _require_operator_token(request: Request) -> str:
    settings = get_settings()
    if not settings.operator_token_list:
        raise HTTPException(status_code=503, detail="Operator access is not configured")

    auth_header = request.headers.get("authorization", "")
    token = ""
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    token = (
        token
        or request.headers.get("x-operator-token", "").strip()
        or request.query_params.get("token", "").strip()
        or request.cookies.get("operator_token", "")
    )
    if token not in settings.operator_token_list:
        raise HTTPException(status_code=401, detail="Operator token required")
    return token


async def _operator_summary_payload(db: AsyncSession) -> dict:
    archive = await get_or_create_hosted_archive(db)
    backup_health = get_backup_health()
    usage = compute_archive_storage_usage()

    persons_total = await db.scalar(select(func.count()).select_from(Person))
    media_total = await db.scalar(select(func.count()).select_from(Media))
    pending_accounts = await db.scalar(
        select(func.count()).select_from(Person).where(Person.account_state == AccountState.pending.value)
    )
    active_sessions = await db.scalar(select(func.count()).select_from(UserSession))

    summary = build_operator_archive_summary(
        archive,
        backup_health=backup_health,
        usage=usage,
    )
    summary.update(
        {
            "persons_total": persons_total or 0,
            "media_total": media_total or 0,
            "pending_accounts": pending_accounts or 0,
            "active_sessions": active_sessions or 0,
            "storage_total_human": format_bytes(summary["storage_total_bytes"]),
            "storage_quota_human": format_bytes(summary["storage_quota_bytes"]),
        }
    )
    return summary


def _hosted_enabled_or_404() -> None:
    if not hosted_archive_enabled():
        raise HTTPException(status_code=404, detail="Hosted archive platform is disabled")


@router.get("/api/operator/archive")
async def get_operator_archive(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    _hosted_enabled_or_404()
    _require_operator_token(request)
    return await _operator_summary_payload(db)


@router.post("/api/operator/archive/provision")
async def provision_operator_archive(
    body: HostedArchiveProvisionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    _hosted_enabled_or_404()
    _require_operator_token(request)
    archive = await provision_hosted_archive(
        db,
        actor_id=None,
        archive_name=body.archive_name,
        owner_email=body.owner_email,
        base_url=body.base_url,
        plan_code=body.plan_code,
        support_notes=body.support_notes,
    )
    await log_audit(
        db,
        actor_id=None,
        action="create",
        entity_type="hosted_archive",
        entity_id=archive.id,
        new_value={
            "archive_key": archive.archive_key,
            "owner_email": archive.owner_email,
            "plan_code": archive.plan_code,
        },
    )
    return await _operator_summary_payload(db)


@router.post("/api/operator/archive/lifecycle")
async def update_operator_archive_lifecycle(
    body: HostedArchiveLifecycleRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    _hosted_enabled_or_404()
    _require_operator_token(request)
    archive = await get_or_create_hosted_archive(db)
    try:
        await set_archive_lifecycle_state(
            db,
            archive=archive,
            lifecycle_state=body.lifecycle_state,
            actor_id=None,
            reason=body.reason,
            export_state=body.export_state,
            deletion_state=body.deletion_state,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    await log_audit(
        db,
        actor_id=None,
        action="update",
        entity_type="hosted_archive",
        entity_id=archive.id,
        new_value={
            "lifecycle_state": archive.lifecycle_state,
            "reason": archive.lifecycle_reason,
            "export_state": archive.export_state,
            "deletion_state": archive.deletion_state,
        },
    )
    return await _operator_summary_payload(db)


@router.get("/operator", response_class=HTMLResponse)
async def operator_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    _hosted_enabled_or_404()
    token = _require_operator_token(request)
    summary = await _operator_summary_payload(db)
    return templates.TemplateResponse(
        "operator.html",
        {
            "request": request,
            "operator_token": token,
            "summary": summary,
            "app_theme": get_runtime_theme_from_app(request.app),
            "current_user": None,
            "locale": "en",
            "t": lambda key: translate(key, "en"),
            "brand_display_name": get_runtime_theme_from_app(request.app)["brand_display_name"],
            "demo_mode": False,
        },
    )


@router.get("/api/billing/hosted-archive")
async def get_hosted_archive_billing_state(
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    _hosted_enabled_or_404()
    archive = await get_or_create_hosted_archive(db, actor_id=current_user.id)
    usage_snapshot = archive_usage_snapshot(archive)
    entitlement = get_plan_entitlement(archive.plan_code)
    return {
        "archive_key": archive.archive_key,
        "archive_name": archive.archive_name,
        "plan_code": archive.plan_code,
        "plan_label": entitlement.label,
        "monthly_price_display": entitlement.monthly_price_display,
        "billing_status": archive.billing_status,
        "billing_provider": archive.billing_provider,
        "lifecycle_state": archive.lifecycle_state,
        "storage_total_bytes": usage_snapshot["usage"].total_bytes,
        "storage_total_human": format_bytes(usage_snapshot["usage"].total_bytes),
        "storage_quota_bytes": usage_snapshot["quota_bytes"],
        "storage_quota_human": format_bytes(usage_snapshot["quota_bytes"]),
        "quota_exceeded": usage_snapshot["quota_exceeded"],
        "quota_remaining_bytes": usage_snapshot["quota_remaining_bytes"],
    }


@router.post("/api/billing/checkout")
async def start_checkout(
    body: BillingCheckoutRequest,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    _hosted_enabled_or_404()
    archive = await get_or_create_hosted_archive(db, actor_id=current_user.id)
    try:
        session = await create_checkout_session(archive, plan_code=body.plan_code)
    except BillingConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    await log_audit(
        db,
        actor_id=current_user.id,
        action="create",
        entity_type="billing_checkout",
        entity_id=archive.id,
        new_value={"plan_code": body.plan_code},
    )
    return {
        "status": "ok",
        "checkout_url": session.checkout_url,
        "session_id": session.session_id,
    }


@router.post("/api/billing/portal")
async def open_billing_portal(
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    _hosted_enabled_or_404()
    archive = await get_or_create_hosted_archive(db, actor_id=current_user.id)
    try:
        portal_url = await create_billing_portal_session(archive)
    except BillingConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"status": "ok", "portal_url": portal_url}


@router.post("/api/billing/stripe/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    _hosted_enabled_or_404()
    payload = await request.body()
    signature_header = request.headers.get("stripe-signature", "")
    try:
        event = verify_stripe_webhook_signature(payload, signature_header)
        archive = await apply_stripe_event(db, event)
    except StripeWebhookError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if archive:
        await log_audit(
            db,
            actor_id=None,
            action="update",
            entity_type="hosted_archive_billing",
            entity_id=archive.id,
            new_value={
                "billing_status": archive.billing_status,
                "plan_code": archive.plan_code,
                "stripe_subscription_id": archive.stripe_subscription_id,
            },
        )
    return {"status": "ok"}
