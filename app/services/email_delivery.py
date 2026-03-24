from __future__ import annotations

import html
import logging
from datetime import datetime

import httpx
from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger(__name__)


class InviteDeliveryResult(BaseModel):
    status: str
    provider: str | None = None
    message_id: str | None = None
    error: str | None = None


async def send_invite_email(
    *,
    recipient_email: str,
    recipient_name: str,
    invite_url: str,
    invited_by_name: str,
    expires_at: datetime,
) -> InviteDeliveryResult:
    settings = get_settings()
    if not settings.resend_enabled:
        return InviteDeliveryResult(status="not_configured")

    payload = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [recipient_email],
        "subject": f"{invited_by_name} invited you to join Family Book",
        "html": _invite_email_html(
            recipient_name=recipient_name,
            invite_url=invite_url,
            invited_by_name=invited_by_name,
            expires_at=expires_at,
        ),
        "text": _invite_email_text(
            recipient_name=recipient_name,
            invite_url=invite_url,
            invited_by_name=invited_by_name,
            expires_at=expires_at,
        ),
    }
    if settings.RESEND_REPLY_TO_EMAIL.strip():
        payload["reply_to"] = settings.RESEND_REPLY_TO_EMAIL.strip()

    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers=headers,
                json=payload,
            )
    except httpx.HTTPError as exc:
        logger.warning("Resend invite delivery failed before response: %s", exc)
        return InviteDeliveryResult(status="failed", provider="resend", error=str(exc))

    if response.is_success:
        body = response.json()
        message_id = body.get("id") if isinstance(body, dict) else None
        logger.info("Invite email sent to %s via Resend", recipient_email)
        return InviteDeliveryResult(
            status="sent",
            provider="resend",
            message_id=message_id if isinstance(message_id, str) else None,
        )

    error = _extract_error_message(response)
    logger.warning(
        "Resend invite delivery failed for %s with status %s: %s",
        recipient_email,
        response.status_code,
        error,
    )
    return InviteDeliveryResult(
        status="failed",
        provider="resend",
        error=error,
    )


def _invite_email_html(
    *,
    recipient_name: str,
    invite_url: str,
    invited_by_name: str,
    expires_at: datetime,
) -> str:
    expires_label = expires_at.strftime("%B %d, %Y")
    safe_recipient_name = html.escape(recipient_name)
    safe_invited_by_name = html.escape(invited_by_name)
    safe_invite_url = html.escape(invite_url, quote=True)
    safe_expires_label = html.escape(expires_label)
    return (
        "<div style=\"font-family:Arial,sans-serif;line-height:1.5;color:#24312b;\">"
        f"<p>Hello {safe_recipient_name},</p>"
        f"<p>{safe_invited_by_name} invited you to join Family Book, your private family archive.</p>"
        f"<p><a href=\"{safe_invite_url}\" "
        "style=\"display:inline-block;padding:12px 18px;border-radius:999px;"
        "background:#2f5d4b;color:#ffffff;text-decoration:none;font-weight:600;\">"
        "Accept your invite</a></p>"
        f"<p>This invite expires on {safe_expires_label}.</p>"
        f"<p>If the button does not work, use this link:<br>{safe_invite_url}</p>"
        "</div>"
    )


def _invite_email_text(
    *,
    recipient_name: str,
    invite_url: str,
    invited_by_name: str,
    expires_at: datetime,
) -> str:
    expires_label = expires_at.strftime("%B %d, %Y")
    return (
        f"Hello {recipient_name},\n\n"
        f"{invited_by_name} invited you to join Family Book.\n\n"
        f"Accept your invite: {invite_url}\n\n"
        f"This invite expires on {expires_label}.\n"
    )


def _extract_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict):
        for key in ("message", "error"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return f"Resend returned {response.status_code}"
