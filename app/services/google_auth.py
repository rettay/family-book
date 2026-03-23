from collections.abc import Mapping

from google.auth.transport.requests import Request
from google.oauth2 import id_token

from app.config import get_settings


class GoogleAuthError(Exception):
    """Raised when a Google credential cannot be trusted or used."""


def verify_google_credential(credential: str) -> dict[str, str | bool | None]:
    settings = get_settings()
    client_id = settings.GOOGLE_CLIENT_ID.strip()
    if not client_id:
        raise GoogleAuthError("Google Sign-In is not configured on this server.")
    if not credential:
        raise GoogleAuthError("Missing Google credential.")

    try:
        payload = id_token.verify_oauth2_token(credential, Request(), client_id)
    except Exception as exc:  # pragma: no cover - exercised via monkeypatch in tests
        raise GoogleAuthError("Invalid Google credential.") from exc

    if payload.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}:
        raise GoogleAuthError("Unexpected Google token issuer.")

    hosted_domain = settings.GOOGLE_HOSTED_DOMAIN.strip().lower()
    token_hd = str(payload.get("hd") or "").lower()
    if hosted_domain and token_hd != hosted_domain:
        raise GoogleAuthError("Google account is not in the allowed hosted domain.")

    sub = payload.get("sub")
    if not sub:
        raise GoogleAuthError("Google credential is missing a subject identifier.")

    return {
        "sub": str(sub),
        "email": _optional_str(payload, "email"),
        "email_verified": bool(payload.get("email_verified")),
        "name": _optional_str(payload, "name"),
        "picture": _optional_str(payload, "picture"),
        "hd": token_hd or None,
    }


def _optional_str(payload: Mapping[str, object], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    return str(value)
