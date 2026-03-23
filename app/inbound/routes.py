"""
Inbound email webhook — Envelope API.

POST /api/inbound/envelope

Receives forwarded emails to family@martin.fm, extracts photos from
attachments, matches sender email to Person, creates Moments.

HMAC signature verification via X-Envelope-Signature header.
"""

import hashlib
import hmac
import ipaddress
import logging
import os
import socket
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.config import get_settings
from app.services.io_limits import SizeLimitExceeded, read_response_limited

logger = logging.getLogger(__name__)

router = APIRouter(tags=["inbound"])


class EnvelopeAttachment(BaseModel):
    filename: str
    content_type: str
    url: str


class EnvelopePayload(BaseModel):
    sender: str = ""  # Envelope uses 'from' but that's a Python keyword
    subject: str = ""
    text_body: str = ""
    attachments: list[EnvelopeAttachment] = []


ALLOWED_ATTACHMENT_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/gif",
    "video/mp4", "video/webm",
}


@router.post("/api/inbound/envelope")
async def envelope_webhook(request: Request):
    """Receive inbound email from Envelope."""
    settings = get_settings()
    secret = settings.ENVELOPE_WEBHOOK_SECRET

    if not secret:
        raise HTTPException(status_code=500, detail="Webhook not configured")

    # Verify HMAC signature
    body = await request.body()
    signature = request.headers.get("X-Envelope-Signature", "")
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse payload
    payload = await request.json()
    sender_email = payload.get("from", payload.get("sender", ""))
    subject = payload.get("subject", "")
    attachments = payload.get("attachments", [])

    logger.info(
        "Inbound email from=%s subject=%s attachments=%d",
        sender_email, subject, len(attachments),
    )

    if attachments and not settings.envelope_allowed_host_list:
        raise HTTPException(
            status_code=503,
            detail="Attachment downloads are not configured for this environment",
        )

    # Download and save attachments
    saved_files = []
    async with httpx.AsyncClient(timeout=30, follow_redirects=False) as http:
        for att in attachments:
            content_type = att.get("content_type", "")
            if content_type not in ALLOWED_ATTACHMENT_TYPES:
                continue

            url = att.get("url", "")
            if not url:
                continue
            if not _is_allowed_attachment_url(url, settings.envelope_allowed_host_list):
                logger.warning("Rejected attachment URL outside allowlist: %s", url)
                continue

            try:
                async with http.stream("GET", url) as resp:
                    resp.raise_for_status()
                    content_length = int(resp.headers.get("content-length", "0") or 0)
                    if content_length and content_length > settings.ENVELOPE_MAX_ATTACHMENT_BYTES:
                        raise SizeLimitExceeded(
                            f"Attachment exceeds {settings.ENVELOPE_MAX_ATTACHMENT_BYTES} bytes"
                        )
                    content = await read_response_limited(
                        resp,
                        settings.ENVELOPE_MAX_ATTACHMENT_BYTES,
                    )

                file_hash = hashlib.sha256(content).hexdigest()
                ext = _ext_from_mime(content_type)
                filename = f"email_{file_hash[:16]}{ext}"

                data_dir = getattr(settings, "resolved_data_dir", settings.DATA_DIR)
                media_dir = os.path.join(data_dir, "media")
                os.makedirs(media_dir, exist_ok=True)
                file_path = os.path.join(media_dir, filename)

                with open(file_path, "wb") as f:
                    f.write(content)

                saved_files.append({
                    "filename": filename,
                    "file_hash": file_hash,
                    "content_type": content_type,
                    "size": len(content),
                })
                logger.info("Saved email attachment: %s (%d bytes)", filename, len(content))
            except SizeLimitExceeded:
                logger.warning("Rejected oversized attachment: %s", att.get("filename"))
            except Exception:
                logger.exception("Failed to download attachment: %s", att.get("filename"))

    # NOTE: Person matching (sender_email → Person.contact_email) and
    # Media + Moment record creation is a Phase 2 merge point.
    # Files are saved to data/media/ for Phase 2 to pick up.

    return {
        "status": "ok",
        "sender": sender_email,
        "attachments_saved": len(saved_files),
        "files": saved_files,
    }


def _ext_from_mime(content_type: str) -> str:
    return {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "video/mp4": ".mp4",
        "video/webm": ".webm",
    }.get(content_type, ".bin")


def _is_allowed_attachment_url(url: str, allowed_hosts: list[str]) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"https"}:
        return False
    if not parsed.hostname:
        return False

    hostname = parsed.hostname.lower()
    if not any(hostname == allowed or hostname.endswith(f".{allowed}") for allowed in allowed_hosts):
        return False

    try:
        address_info = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return False

    for entry in address_info:
        ip = ipaddress.ip_address(entry[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            return False

    return True
