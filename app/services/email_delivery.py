from __future__ import annotations

import asyncio
import html
import logging
import smtplib
from datetime import datetime
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from typing import Callable

from pydantic import BaseModel

from app.config import get_settings
from app.services.prompt_service import render_weekly_digest_html, render_weekly_digest_text

logger = logging.getLogger(__name__)


class EmailDeliveryResult(BaseModel):
    status: str
    provider: str | None = None
    message_id: str | None = None
    error: str | None = None


InviteDeliveryResult = EmailDeliveryResult

SMTPFactory = Callable[..., smtplib.SMTP]


async def send_email(
    *,
    recipient_email: str,
    subject: str,
    html_body: str,
    text_body: str,
    smtp_factory: SMTPFactory | None = None,
) -> EmailDeliveryResult:
    settings = get_settings()
    if not settings.smtp_enabled:
        return EmailDeliveryResult(status="not_configured")

    message_id = make_msgid(domain=_message_id_domain(settings.SMTP_FROM))
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM.strip()
    message["To"] = recipient_email
    message["Subject"] = subject
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = message_id
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

    try:
        await asyncio.to_thread(
            _send_message_sync,
            message,
            recipient_email,
            smtp_factory or _default_smtp_factory,
        )
    except (OSError, smtplib.SMTPException) as exc:
        safe_error = _safe_smtp_error(exc)
        logger.warning("SMTP email delivery failed for %s: %s", recipient_email, safe_error)
        return EmailDeliveryResult(status="failed", provider="smtp", error=safe_error)

    logger.info("Email sent to %s via SMTP", recipient_email)
    return EmailDeliveryResult(
        status="sent",
        provider="smtp",
        message_id=message_id.strip("<>"),
    )


async def send_invite_email(
    *,
    recipient_email: str,
    recipient_name: str,
    invite_url: str,
    invited_by_name: str,
    expires_at: datetime,
    family_name: str = "Family Book",
) -> InviteDeliveryResult:
    return await send_email(
        recipient_email=recipient_email,
        subject=f"{invited_by_name} invited you to join {family_name}",
        html_body=_invite_email_html(
            recipient_name=recipient_name,
            invite_url=invite_url,
            invited_by_name=invited_by_name,
            expires_at=expires_at,
            family_name=family_name,
        ),
        text_body=_invite_email_text(
            recipient_name=recipient_name,
            invite_url=invite_url,
            invited_by_name=invited_by_name,
            expires_at=expires_at,
            family_name=family_name,
        ),
    )


async def send_magic_link_email(
    *,
    recipient_email: str,
    recipient_name: str,
    magic_link_url: str,
    expires_minutes: int,
    family_name: str = "Family Book",
) -> EmailDeliveryResult:
    return await send_email(
        recipient_email=recipient_email,
        subject=f"Your sign-in link for {family_name}",
        html_body=_magic_link_email_html(
            recipient_name=recipient_name,
            magic_link_url=magic_link_url,
            expires_minutes=expires_minutes,
            family_name=family_name,
        ),
        text_body=_magic_link_email_text(
            recipient_name=recipient_name,
            magic_link_url=magic_link_url,
            expires_minutes=expires_minutes,
            family_name=family_name,
        ),
    )


async def send_weekly_digest_email(
    *,
    recipient_email: str,
    recipient_name: str,
    digest: dict[str, list[dict]],
    family_name: str = "Family Book",
) -> EmailDeliveryResult:
    return await send_email(
        recipient_email=recipient_email,
        subject=f"{family_name} weekly digest",
        html_body=render_weekly_digest_html(
            recipient_name=recipient_name,
            digest=digest,
            family_name=family_name,
        ),
        text_body=render_weekly_digest_text(
            recipient_name=recipient_name,
            digest=digest,
            family_name=family_name,
        ),
    )


def _send_message_sync(
    message: EmailMessage,
    recipient_email: str,
    smtp_factory: SMTPFactory,
) -> None:
    settings = get_settings()
    host = settings.SMTP_HOST.strip()
    port = int(settings.SMTP_PORT)
    username = settings.SMTP_USER.strip()
    password = settings.SMTP_PASS
    sender = settings.SMTP_FROM.strip()

    with smtp_factory(host, port, timeout=10) as smtp:
        if port != 465:
            smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message, from_addr=sender, to_addrs=[recipient_email])


def _default_smtp_factory(host: str, port: int, timeout: int):
    if port == 465:
        return smtplib.SMTP_SSL(host, port, timeout=timeout)
    return smtplib.SMTP(host, port, timeout=timeout)


def _safe_smtp_error(exc: BaseException) -> str:
    settings = get_settings()
    text = str(exc) or exc.__class__.__name__
    for secret in (settings.SMTP_PASS, settings.SMTP_USER):
        if secret:
            text = text.replace(secret, "[redacted]")
    return text[:500]


def _message_id_domain(sender: str) -> str | None:
    if "@" not in sender:
        return None
    domain = sender.rsplit("@", 1)[1].strip(" >")
    return domain or None


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
        '<tr><td style="background-color:#2d5016;padding:28px 32px;text-align:center;">'
        f'<h1 style="margin:0;color:#fffaf1;font-size:22px;font-weight:700;'
        f'font-family:Georgia,serif;letter-spacing:0.02em;">{safe_family_name}</h1>'
        '</td></tr>'
        '<tr><td style="padding:32px 32px 24px;text-align:center;">'
        '<p style="margin:0 0 8px;font-size:26px;">&#127807;</p>'
        '<h2 style="margin:0 0 16px;font-size:20px;color:#2d5016;'
        'font-family:Georgia,serif;font-weight:600;">Join Your Family Tree</h2>'
        f'<p style="margin:0 0 8px;font-size:15px;color:#5a5347;">Hello {safe_recipient_name},</p>'
        f'<p style="margin:0 0 24px;font-size:15px;color:#5a5347;line-height:1.6;">'
        f'You\'ve been invited by <strong style="color:#2d5016;">{safe_invited_by_name}</strong> '
        f'to join the family archive&mdash;a private space for your family tree, photos, '
        f'stories, and records.</p>'
        f'<a href="{safe_invite_url}" style="display:inline-block;padding:14px 36px;'
        'background-color:#2d5016;color:#fffaf1;text-decoration:none;font-weight:700;'
        'font-size:16px;border-radius:8px;font-family:Arial,sans-serif;'
        'letter-spacing:0.02em;">Accept Your Invite</a>'
        '</td></tr>'
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


def _magic_link_email_html(
    *,
    recipient_name: str,
    magic_link_url: str,
    expires_minutes: int,
    family_name: str,
) -> str:
    safe_recipient_name = html.escape(recipient_name)
    safe_magic_link_url = html.escape(magic_link_url, quote=True)
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
        '<tr><td style="background-color:#2d5016;padding:28px 32px;text-align:center;">'
        f'<h1 style="margin:0;color:#fffaf1;font-size:22px;font-weight:700;'
        f'font-family:Georgia,serif;letter-spacing:0.02em;">{safe_family_name}</h1>'
        '</td></tr>'
        '<tr><td style="padding:32px;text-align:center;">'
        '<h2 style="margin:0 0 16px;font-size:20px;color:#2d5016;'
        'font-family:Georgia,serif;font-weight:600;">Sign in to your family archive</h2>'
        f'<p style="margin:0 0 8px;font-size:15px;color:#5a5347;">Hello {safe_recipient_name},</p>'
        '<p style="margin:0 0 24px;font-size:15px;color:#5a5347;line-height:1.6;">'
        'Use this one-time link to sign in. It only works once.</p>'
        f'<a href="{safe_magic_link_url}" style="display:inline-block;padding:14px 36px;'
        'background-color:#2d5016;color:#fffaf1;text-decoration:none;font-weight:700;'
        'font-size:16px;border-radius:8px;font-family:Arial,sans-serif;'
        'letter-spacing:0.02em;">Sign In</a>'
        '</td></tr>'
        '<tr><td style="padding:16px 32px 28px;text-align:center;'
        'border-top:1px solid #e8e0d4;">'
        f'<p style="margin:0 0 8px;font-size:13px;color:#8a8078;">'
        f'This link expires in {expires_minutes} minutes.</p>'
        f'<p style="margin:0;font-size:12px;color:#a09888;word-break:break-all;">'
        f'If the button doesn\'t work, copy this link:<br>'
        f'<a href="{safe_magic_link_url}" style="color:#2d5016;">{safe_magic_link_url}</a></p>'
        '</td></tr>'
        '</table>'
        '</td></tr></table>'
        '</body></html>'
    )


def _magic_link_email_text(
    *,
    recipient_name: str,
    magic_link_url: str,
    expires_minutes: int,
    family_name: str,
) -> str:
    return (
        f"Hello {recipient_name},\n\n"
        f"Use this one-time link to sign in to {family_name}:\n\n"
        f"{magic_link_url}\n\n"
        f"This link expires in {expires_minutes} minutes and only works once.\n"
    )
