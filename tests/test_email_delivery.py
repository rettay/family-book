from datetime import datetime, timezone

from app.services.email_delivery import _invite_email_html


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
