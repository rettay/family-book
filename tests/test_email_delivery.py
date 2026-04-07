from datetime import datetime, timezone

import pytest

from app.services.email_delivery import _invite_email_html, send_email


def test_invite_email_html_escapes_profile_derived_values():
    html = _invite_email_html(
        recipient_name='Jane <img src=x onerror=alert(1)>',
        invite_url='https://family.example/invite/<bad>?q="quoted"',
        invited_by_name='Tyler & Co',
        expires_at=datetime(2026, 3, 24, tzinfo=timezone.utc),
    )

    assert '<img src=x onerror=alert(1)>' not in html
    assert 'Jane &lt;img src=x onerror=alert(1)&gt;' in html
    assert 'Tyler &amp; Co' in html
    assert 'https://family.example/invite/&lt;bad&gt;?q=&quot;quoted&quot;' in html


@pytest.mark.asyncio
async def test_smtp_email_delivery_sends_when_configured(monkeypatch):
    sent = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            sent["host"] = host
            sent["port"] = port
            sent["timeout"] = timeout
            sent["starttls"] = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            sent["starttls"] = True

        def login(self, username, password):
            sent["username"] = username
            sent["password"] = password

        def send_message(self, message, from_addr, to_addrs):
            sent["subject"] = message["Subject"]
            sent["from_addr"] = from_addr
            sent["to_addrs"] = to_addrs

    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "invites@example.com")
    monkeypatch.setenv("SMTP_PASS", "smtp-secret")
    monkeypatch.setenv("SMTP_FROM", "Family Book <invites@example.com>")

    result = await send_email(
        recipient_email="jane@example.com",
        subject="Welcome",
        html_body="<p>Hello</p>",
        text_body="Hello",
        smtp_factory=FakeSMTP,
    )

    assert result.status == "sent"
    assert result.provider == "smtp"
    assert sent["host"] == "smtp.example.com"
    assert sent["starttls"] is True
    assert sent["username"] == "invites@example.com"
    assert sent["password"] == "smtp-secret"
    assert sent["to_addrs"] == ["jane@example.com"]


@pytest.mark.asyncio
async def test_smtp_email_delivery_missing_config_returns_manual_fallback(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASS", raising=False)
    monkeypatch.delenv("SMTP_FROM", raising=False)

    result = await send_email(
        recipient_email="jane@example.com",
        subject="Welcome",
        html_body="<p>Hello</p>",
        text_body="Hello",
        smtp_factory=lambda *args, **kwargs: None,
    )

    assert result.status == "not_configured"
    assert result.provider is None


@pytest.mark.asyncio
async def test_smtp_email_delivery_failure_redacts_secret(monkeypatch):
    class FailingSMTP:
        def __init__(self, host, port, timeout):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            pass

        def login(self, username, password):
            raise OSError(f"auth failed for {username} using {password}")

    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "invites@example.com")
    monkeypatch.setenv("SMTP_PASS", "smtp-secret")
    monkeypatch.setenv("SMTP_FROM", "Family Book <invites@example.com>")

    result = await send_email(
        recipient_email="jane@example.com",
        subject="Welcome",
        html_body="<p>Hello</p>",
        text_body="Hello",
        smtp_factory=FailingSMTP,
    )

    assert result.status == "failed"
    assert result.provider == "smtp"
    assert "smtp-secret" not in (result.error or "")
    assert "invites@example.com" not in (result.error or "")
