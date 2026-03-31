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
    family_name: str = "Family Book",
) -> InviteDeliveryResult:
    settings = get_settings()
    if not settings.resend_enabled:
        return InviteDeliveryResult(status="not_configured")

    payload = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [recipient_email],
        "subject": f"{invited_by_name} invited you to join {family_name}",
        "html": _invite_email_html(
            recipient_name=recipient_name,
            invite_url=invite_url,
            invited_by_name=invited_by_name,
            expires_at=expires_at,
            family_name=family_name,
        ),
        "text": _invite_email_text(
            recipient_name=recipient_name,
            invite_url=invite_url,
            invited_by_name=invited_by_name,
            expires_at=expires_at,
            family_name=family_name,
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
    family_name: str = "Family Book",
) -> str:
    expires_label = expires_at.strftime("%B %d, %Y")
    safe_recipient_name = html.escape(recipient_name)
    safe_invited_by_name = html.escape(invited_by_name)
    safe_invite_url = html.escape(invite_url, quote=True)
    safe_expires_label = html.escape(expires_label)
    safe_family_name = html.escape(family_name)

    return (
        '<!DOCTYPE html>'
        '<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1"></head>'
        '<body style="margin:0;padding:0;background-color:#f5f1eb;font-family:Georgia,serif;">'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
        'style="background-color:#f5f1eb;padding:32px 16px;">'
        '<tr><td align="center">'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
        'style="max-width:520px;background-color:#fffaf1;border-radius:12px;'
        'border:1px solid #e8e0d4;overflow:hidden;">'
        # Header
        '<tr><td style="background-color:#2d5016;padding:28px 32px;text-align:center;">'
        f'<h1 style="margin:0;color:#fffaf1;font-size:22px;font-weight:700;'
        f'font-family:Georgia,serif;letter-spacing:0.02em;">{safe_family_name}</h1>'
        '</td></tr>'
        # Body
        '<tr><td style="padding:32px 32px 24px;text-align:center;">'
        '<p style="margin:0 0 8px;font-size:26px;">&#127807;</p>'
        '<h2 style="margin:0 0 16px;font-size:20px;color:#2d5016;'
        'font-family:Georgia,serif;font-weight:600;">Join Your Family Tree</h2>'
        f'<p style="margin:0 0 8px;font-size:15px;color:#5a5347;">Hello {safe_recipient_name},</p>'
        f'<p style="margin:0 0 24px;font-size:15px;color:#5a5347;line-height:1.6;">'
        f'You\'ve been invited by <strong style="color:#2d5016;">{safe_invited_by_name}</strong> '
        f'to join the family archive&mdash;a private space for your family tree, photos, '
        f'stories, and records.</p>'
        # CTA Button
        f'<a href="{safe_invite_url}" style="display:inline-block;padding:14px 36px;'
        'background-color:#2d5016;color:#fffaf1;text-decoration:none;font-weight:700;'
        'font-size:16px;border-radius:8px;font-family:Arial,sans-serif;'
        'letter-spacing:0.02em;">Accept Your Invite</a>'
        '</td></tr>'
        # Footer
        '<tr><td style="padding:16px 32px 28px;text-align:center;'
        'border-top:1px solid #e8e0d4;">'
        f'<p style="margin:0 0 8px;font-size:13px;color:#8a8078;">'
        f'This invite expires on {safe_expires_label}.</p>'
        f'<p style="margin:0;font-size:12px;color:#a09888;word-break:break-all;">'
        f'If the button doesn\'t work, copy this link:<br>'
        f'<a href="{safe_invite_url}" style="color:#2d5016;">{safe_invite_url}</a></p>'
        '</td></tr>'
        '</table>'
        '</td></tr></table>'
        '</body></html>'
    )


def _invite_email_text(
    *,
    recipient_name: str,
    invite_url: str,
    invited_by_name: str,
    expires_at: datetime,
    family_name: str = "Family Book",
) -> str:
    expires_label = expires_at.strftime("%B %d, %Y")
    return (
        f"Hello {recipient_name},\n\n"
        f"{invited_by_name} invited you to join {family_name}.\n\n"
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
