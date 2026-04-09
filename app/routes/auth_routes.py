import json
import logging
import secrets
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from webauthn.helpers.exceptions import (
    InvalidAuthenticationResponse,
    InvalidRegistrationResponse,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from app.auth import SESSION_COOKIE_NAME, get_current_user, require_admin, require_auth
from app.config import get_settings
from app.database import get_db
from app.models.auth import AuthMethod, Invite, PasskeyChallenge, PasskeyCredential
from app.models.person import AccountState, Person, PersonLifecycleState
from app.roles import get_person_role, is_admin_actor
from app.services.audit_service import log_audit
from app.services.google_auth import GoogleAuthError, verify_google_credential
from app.services.email_delivery import (
    EmailDeliveryResult,
    send_invite_email,
    send_magic_link_email,
)
from app.services.auth_service import (
    MAGIC_LINK_EXPIRY_MINUTES,
    authenticate_google_identity,
    claim_invite,
    create_invite,
    create_magic_link,
    create_session,
    delete_session,
    delete_session_by_id,
    delete_all_sessions_for_person,
    find_magic_link_person_by_email,
    get_magic_link_rejection_reason,
    get_invite_by_token,
    get_invite_rejection_reason,
    validate_magic_link,
)
from app.services.field_protection import contact_email_lookup_hash, normalize_email_for_lookup
from app.services.theme_service import (
    DEFAULT_THEME_SETTINGS,
    ThemeSettingsPayload,
    get_or_create_theme_settings_record,
    get_runtime_theme_from_app,
    sync_runtime_theme,
)

router = APIRouter(tags=["auth"])
logger = logging.getLogger(__name__)


class GoogleCredentialRequest(BaseModel):
    credential: str


class MagicLinkRequest(BaseModel):
    email: str
    return_to: str | None = None


class AdminMagicLinkRequest(BaseModel):
    send_email: bool = True
    return_to: str | None = None


class PasskeyRegistrationVerifyRequest(BaseModel):
    challenge_id: str
    credential: dict
    label: str | None = None


class PasskeyAuthenticationVerifyRequest(BaseModel):
    challenge_id: str
    credential: dict
    return_to: str | None = None


class AdminInviteResponse(BaseModel):
    id: str
    person_id: str
    contact_email: str | None
    invite_url: str | None
    claimed_at: str | None
    revoked: bool
    expires_at: str
    delivery_status: str
    delivery_provider: str | None = None
    delivery_message_id: str | None = None
    delivery_error: str | None = None


class MagicLinkPublicResponse(BaseModel):
    status: str
    message: str


class AdminMagicLinkResponse(BaseModel):
    person_id: str
    contact_email: str | None
    magic_link_url: str
    delivery_status: str
    delivery_provider: str | None = None
    delivery_message_id: str | None = None
    delivery_error: str | None = None


class PasskeyCredentialResponse(BaseModel):
    id: str
    label: str
    created_at: str
    last_used_at: str | None = None


MAGIC_LINK_GENERIC_MESSAGE = (
    "If that email matches an active family member, we sent a sign-in link."
)
MAGIC_LINK_REQUEST_LIMIT = 3
MAGIC_LINK_REQUEST_WINDOW_SECONDS = 15 * 60
_magic_link_request_windows: dict[str, list[float]] = defaultdict(list)


def _set_session_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    is_secure = settings.BASE_URL.startswith("https")
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        max_age=30 * 24 * 3600,
        path="/",
    )


def _safe_return_to(value: str | None) -> str:
    if value and value.startswith("/") and not value.startswith("//"):
        return value
    return "/tree"


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _magic_link_url(raw_token: str, return_to: str | None = None) -> str:
    settings = get_settings()
    base_url = f"{settings.BASE_URL.rstrip('/')}/auth/magic-link/{raw_token}"
    safe_return_to = _safe_return_to(return_to)
    if safe_return_to == "/tree":
        return base_url
    return f"{base_url}?{urlencode({'return_to': safe_return_to})}"


def _passkey_options_response(challenge: PasskeyChallenge, options) -> JSONResponse:
    payload = json.loads(options_to_json(options))
    payload["challenge_id"] = challenge.id
    return JSONResponse(payload)


async def _get_unused_passkey_challenge(
    db: AsyncSession,
    challenge_id: str,
    ceremony: str,
    person_id: str | None = None,
) -> PasskeyChallenge:
    challenge = await db.get(PasskeyChallenge, challenge_id)
    now = datetime.now(timezone.utc)
    if (
        not challenge
        or challenge.ceremony != ceremony
        or challenge.used_at is not None
        or _as_aware_utc(challenge.expires_at) <= now
    ):
        raise HTTPException(status_code=400, detail="Passkey challenge is invalid or expired")
    if person_id is not None and challenge.person_id != person_id:
        raise HTTPException(status_code=400, detail="Passkey challenge is invalid or expired")
    return challenge


def _passkey_label(value: str | None) -> str:
    label = (value or "Passkey").strip()
    return label[:120] or "Passkey"


def _magic_link_request_key(email: str | None, request: Request) -> str:
    normalized_email = normalize_email_for_lookup(email) or "blank"
    email_hash = contact_email_lookup_hash(normalized_email) or "blank"
    ip = request.client.host if request.client else "unknown"
    return f"{ip}:{email_hash}"


def _check_magic_link_request_throttle(email: str | None, request: Request) -> None:
    key = _magic_link_request_key(email, request)
    now = time.monotonic()
    cutoff = now - MAGIC_LINK_REQUEST_WINDOW_SECONDS
    window = [stamp for stamp in _magic_link_request_windows[key] if stamp > cutoff]
    if len(window) >= MAGIC_LINK_REQUEST_LIMIT:
        _magic_link_request_windows[key] = window
        logger.warning("Magic-link request throttle exceeded for key %s", key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many sign-in link requests. Try again later.",
            headers={"Retry-After": str(MAGIC_LINK_REQUEST_WINDOW_SECONDS)},
        )
    window.append(now)
    _magic_link_request_windows[key] = window


async def _audit_failed_passkey(
    db: AsyncSession,
    *,
    challenge: PasskeyChallenge,
    action: str,
    reason: str,
    entity_id: str,
    actor_id: str | None = None,
    person_id: str | None = None,
) -> None:
    challenge.used_at = datetime.now(timezone.utc)
    await log_audit(
        db,
        actor_id=actor_id,
        action=action,
        entity_type="passkey",
        entity_id=entity_id,
        new_value={
            "reason": reason,
            "challenge_id": challenge.id,
            "person_id": person_id,
        },
    )


async def _create_and_deliver_magic_link(
    *,
    db: AsyncSession,
    person: Person,
    request: Request,
    return_to: str | None,
    send_email: bool,
    actor_id: str | None,
    source: str,
) -> tuple[str, EmailDeliveryResult]:
    raw_token = await create_magic_link(db, person.id)
    link_url = _magic_link_url(raw_token, return_to)
    app_theme = get_runtime_theme_from_app(request.app)
    delivery = EmailDeliveryResult(status="manual", provider=None)
    if send_email:
        delivery = await send_magic_link_email(
            recipient_email=person.contact_email or "",
            recipient_name=person.display_name,
            magic_link_url=link_url,
            expires_minutes=MAGIC_LINK_EXPIRY_MINUTES,
            family_name=app_theme.get("brand_display_name", "Family Book"),
        )

    await log_audit(
        db,
        actor_id=actor_id,
        action="create",
        entity_type="magic_link",
        entity_id=person.id,
        new_value={
            "person_id": person.id,
            "source": source,
            "sent": send_email,
            "delivery_status": delivery.status,
            "delivery_provider": delivery.provider,
            "ip": request.client.host if request.client else None,
        },
    )
    return link_url, delivery


@router.get("/dev/login")
async def dev_login(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Dev-only login bypass. Active only when DEV_BYPASS_AUTH=true in .env."""
    settings = get_settings()
    if not settings.DEV_BYPASS_AUTH:
        raise HTTPException(status_code=404, detail="Not found")

    # Find the first admin user, or fall back to any active user
    result = await db.execute(
        select(Person).where(
            Person.lifecycle_state == "active",
            or_(Person.is_admin.is_(True), Person.role.in_(["owner", "admin"])),
        ).limit(1)
    )
    person = result.scalar_one_or_none()
    if not person:
        result = await db.execute(
            select(Person).where(Person.lifecycle_state == "active").limit(1)
        )
        person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=500, detail="No active users in database")

    token = await create_session(db, person_id=person.id, auth_method="dev_bypass")
    await db.commit()
    _set_session_cookie(response, token)
    logger.warning("DEV BYPASS: logged in as %s (%s)", person.display_name, person.id)
    return_to = request.query_params.get("return_to", "/tree")
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=return_to, status_code=302)


@router.post("/auth/google")
async def authenticate_with_google(
    body: GoogleCredentialRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Verify a Google ID token and create a family-book session."""
    try:
        claims = verify_google_credential(body.credential)
        person = await authenticate_google_identity(
            db,
            google_sub=str(claims["sub"]),
            email=claims.get("email") if isinstance(claims.get("email"), str) else None,
            email_verified=bool(claims["email_verified"]),
        )
    except GoogleAuthError as exc:
        status_code = 503 if "not configured" in str(exc).lower() else 401
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except ValueError as exc:
        # Map specific error messages to error codes for the login page
        msg = str(exc).lower()
        if "suspended" in msg:
            error_code = "suspended"
        elif "pending" in msg:
            error_code = "pending"
        else:
            error_code = "no_account"
        raise HTTPException(status_code=403, detail=error_code) from exc

    session_token = await create_session(
        db,
        person_id=person.id,
        auth_method=AuthMethod.google_oauth.value,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    person.last_login_at = datetime.now(timezone.utc).isoformat()
    await log_audit(
        db,
        actor_id=person.id,
        action="login",
        entity_type="session",
        entity_id=person.id,
        new_value={
            "auth_method": AuthMethod.google_oauth.value,
            "ip": request.client.host if request.client else None,
        },
    )
    await db.commit()

    _set_session_cookie(response, session_token)
    logger.info("Google authentication succeeded for person %s", person.id)
    return {"status": "ok", "person_id": person.id}


@router.post("/auth/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: Person | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        if current_user:
            await log_audit(
                db,
                actor_id=current_user.id,
                action="logout",
                entity_type="session",
                entity_id=current_user.id,
                new_value={
                    "ip": request.client.host if request.client else None,
                },
            )
        await delete_session(db, token)
        await db.commit()
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    logger.info("Session logout completed")
    return {"status": "ok"}


@router.get("/auth/me")
async def get_me(current_user: Person = Depends(require_auth)):
    return {
        "id": current_user.id,
        "display_name": current_user.display_name,
        "is_admin": is_admin_actor(current_user),
        "role": get_person_role(current_user),
        "branch": current_user.branch,
    }


@router.get("/auth/passkeys", response_model=list[PasskeyCredentialResponse])
async def list_passkeys(
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PasskeyCredential)
        .where(PasskeyCredential.person_id == current_user.id)
        .order_by(PasskeyCredential.created_at.desc())
    )
    return [
        PasskeyCredentialResponse(
            id=credential.id,
            label=credential.label,
            created_at=credential.created_at.isoformat(),
            last_used_at=(
                credential.last_used_at.isoformat() if credential.last_used_at else None
            ),
        )
        for credential in result.scalars().all()
    ]


@router.post("/auth/passkeys/register/options")
async def start_passkey_registration(
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    existing = (
        await db.execute(
            select(PasskeyCredential).where(PasskeyCredential.person_id == current_user.id)
        )
    ).scalars().all()
    challenge_bytes = secrets.token_bytes(32)
    challenge = PasskeyChallenge(
        person_id=current_user.id,
        challenge=bytes_to_base64url(challenge_bytes),
        ceremony="registration",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    db.add(challenge)
    await db.flush()
    options = generate_registration_options(
        rp_id=settings.passkey_rp_id,
        rp_name=settings.PASSKEY_RP_NAME,
        user_id=current_user.id.encode("utf-8"),
        user_name=current_user.contact_email or current_user.display_name,
        user_display_name=current_user.display_name,
        challenge=challenge_bytes,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.PREFERRED,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
        exclude_credentials=[
            PublicKeyCredentialDescriptor(id=base64url_to_bytes(credential.credential_id))
            for credential in existing
        ],
    )
    await db.commit()
    return _passkey_options_response(challenge, options)


@router.post("/auth/passkeys/register/verify", response_model=PasskeyCredentialResponse)
async def finish_passkey_registration(
    body: PasskeyRegistrationVerifyRequest,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    challenge = await _get_unused_passkey_challenge(
        db,
        body.challenge_id,
        "registration",
        person_id=current_user.id,
    )
    try:
        verified = verify_registration_response(
            credential=body.credential,
            expected_challenge=base64url_to_bytes(challenge.challenge),
            expected_rp_id=settings.passkey_rp_id,
            expected_origin=settings.passkey_origin,
            require_user_verification=False,
        )
    except InvalidRegistrationResponse as exc:
        await _audit_failed_passkey(
            db,
            challenge=challenge,
            actor_id=current_user.id,
            action="register_failed",
            entity_id=current_user.id,
            reason=f"invalid_response: {str(exc)[:180]}",
            person_id=current_user.id,
        )
        await db.commit()
        raise HTTPException(status_code=400, detail="Passkey registration failed") from exc

    credential = PasskeyCredential(
        person_id=current_user.id,
        credential_id=bytes_to_base64url(verified.credential_id),
        public_key=bytes_to_base64url(verified.credential_public_key),
        sign_count=verified.sign_count,
        label=_passkey_label(body.label),
        device_type=str(verified.credential_device_type.value),
        backed_up=bool(verified.credential_backed_up),
    )
    challenge.used_at = datetime.now(timezone.utc)
    db.add(credential)
    await db.flush()
    await log_audit(
        db,
        actor_id=current_user.id,
        action="register",
        entity_type="passkey",
        entity_id=credential.id,
        new_value={
            "person_id": current_user.id,
            "credential_id": credential.id,
            "device_type": credential.device_type,
            "backed_up": credential.backed_up,
        },
    )
    await db.commit()
    return PasskeyCredentialResponse(
        id=credential.id,
        label=credential.label,
        created_at=credential.created_at.isoformat(),
        last_used_at=None,
    )


@router.post("/auth/passkeys/authenticate/options")
async def start_passkey_authentication(db: AsyncSession = Depends(get_db)):
    settings = get_settings()
    challenge_bytes = secrets.token_bytes(32)
    challenge = PasskeyChallenge(
        person_id=None,
        challenge=bytes_to_base64url(challenge_bytes),
        ceremony="authentication",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    db.add(challenge)
    await db.flush()
    options = generate_authentication_options(
        rp_id=settings.passkey_rp_id,
        challenge=challenge_bytes,
        user_verification=UserVerificationRequirement.PREFERRED,
    )
    await db.commit()
    return _passkey_options_response(challenge, options)


@router.post("/auth/passkeys/authenticate/verify")
async def finish_passkey_authentication(
    body: PasskeyAuthenticationVerifyRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    challenge = await _get_unused_passkey_challenge(
        db,
        body.challenge_id,
        "authentication",
    )
    credential_id = body.credential.get("id")
    if not isinstance(credential_id, str):
        await _audit_failed_passkey(
            db,
            challenge=challenge,
            action="login_failed",
            entity_id=challenge.id,
            reason="missing_credential_id",
        )
        await db.commit()
        raise HTTPException(status_code=400, detail="Passkey credential is invalid")
    result = await db.execute(
        select(PasskeyCredential).where(PasskeyCredential.credential_id == credential_id)
    )
    credential = result.scalar_one_or_none()
    if not credential:
        await _audit_failed_passkey(
            db,
            challenge=challenge,
            action="login_failed",
            entity_id=challenge.id,
            reason="unknown_credential",
        )
        await db.commit()
        raise HTTPException(status_code=400, detail="Passkey credential is invalid")
    person = await db.get(Person, credential.person_id)
    if (
        not person
        or person.account_state != AccountState.active.value
        or person.lifecycle_state != PersonLifecycleState.active.value
    ):
        await _audit_failed_passkey(
            db,
            challenge=challenge,
            action="login_failed",
            entity_id=credential.id,
            reason="account_unavailable",
            person_id=credential.person_id,
        )
        await db.commit()
        raise HTTPException(status_code=403, detail="Passkey account is unavailable")

    try:
        verified = verify_authentication_response(
            credential=body.credential,
            expected_challenge=base64url_to_bytes(challenge.challenge),
            expected_rp_id=settings.passkey_rp_id,
            expected_origin=settings.passkey_origin,
            credential_public_key=base64url_to_bytes(credential.public_key),
            credential_current_sign_count=credential.sign_count,
            require_user_verification=False,
        )
    except InvalidAuthenticationResponse as exc:
        await _audit_failed_passkey(
            db,
            challenge=challenge,
            actor_id=None,
            action="login_failed",
            entity_id=credential.id,
            reason=f"invalid_response: {str(exc)[:180]}",
            person_id=person.id,
        )
        await db.commit()
        raise HTTPException(status_code=400, detail="Passkey sign-in failed") from exc

    challenge.used_at = datetime.now(timezone.utc)
    credential.sign_count = verified.new_sign_count
    credential.last_used_at = datetime.now(timezone.utc)
    credential.backed_up = bool(verified.credential_backed_up)
    session_token = await create_session(
        db,
        person_id=person.id,
        auth_method=AuthMethod.passkey.value,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    person.last_login_at = datetime.now(timezone.utc).isoformat()
    await log_audit(
        db,
        actor_id=person.id,
        action="login",
        entity_type="session",
        entity_id=person.id,
        new_value={
            "auth_method": AuthMethod.passkey.value,
            "passkey_id": credential.id,
            "ip": request.client.host if request.client else None,
        },
    )
    await db.commit()
    _set_session_cookie(response, session_token)
    return {"status": "ok", "person_id": person.id, "return_to": _safe_return_to(body.return_to)}


@router.delete("/auth/passkeys/{credential_id}")
async def delete_passkey(
    credential_id: str,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    credential = await db.get(PasskeyCredential, credential_id)
    if not credential or credential.person_id != current_user.id:
        raise HTTPException(status_code=404, detail="Passkey not found")
    await log_audit(
        db,
        actor_id=current_user.id,
        action="delete",
        entity_type="passkey",
        entity_id=credential.id,
        new_value={"person_id": current_user.id},
    )
    await db.delete(credential)
    await db.commit()
    return {"status": "ok"}


@router.post("/auth/magic-link/request", response_model=MagicLinkPublicResponse)
async def request_magic_link(
    body: MagicLinkRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    _check_magic_link_request_throttle(body.email, request)
    person = await find_magic_link_person_by_email(db, body.email)
    if not person:
        logger.info(
            "Magic-link request for non-active or unknown email from %s",
            request.client.host if request.client else "unknown",
        )
        return MagicLinkPublicResponse(status="ok", message=MAGIC_LINK_GENERIC_MESSAGE)

    await _create_and_deliver_magic_link(
        db=db,
        person=person,
        request=request,
        return_to=body.return_to,
        send_email=True,
        actor_id=person.id,
        source="self_request",
    )
    await db.commit()
    logger.info("Magic-link request accepted for person %s", person.id)
    return MagicLinkPublicResponse(status="ok", message=MAGIC_LINK_GENERIC_MESSAGE)


@router.post("/auth/magic-link/{token}/claim")
async def claim_magic_link(
    token: str,
    request: Request,
    response: Response,
    return_to: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    person = await validate_magic_link(db, token)
    if not person:
        reason = await get_magic_link_rejection_reason(db, token)
        await log_audit(
            db,
            actor_id=None,
            action="login_failed",
            entity_type="magic_link",
            entity_id="unknown",
            new_value={
                "reason": reason,
                "ip": request.client.host if request.client else None,
            },
        )
        await db.commit()
        raise HTTPException(
            status_code=400,
            detail="This sign-in link is invalid, expired, or already used.",
        )

    session_token = await create_session(
        db,
        person_id=person.id,
        auth_method=AuthMethod.magic_link.value,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    person.last_login_at = datetime.now(timezone.utc).isoformat()
    await log_audit(
        db,
        actor_id=person.id,
        action="login",
        entity_type="session",
        entity_id=person.id,
        new_value={
            "auth_method": AuthMethod.magic_link.value,
            "ip": request.client.host if request.client else None,
        },
    )
    await db.commit()
    _set_session_cookie(response, session_token)
    logger.info("Magic-link authentication succeeded for person %s", person.id)
    return {
        "status": "ok",
        "person_id": person.id,
        "return_to": _safe_return_to(return_to),
    }


@router.post("/api/admin/persons/{person_id}/invite", response_model=AdminInviteResponse, status_code=status.HTTP_201_CREATED)
async def create_person_invite(
    person_id: str,
    request: Request,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    person = await db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if person.lifecycle_state != PersonLifecycleState.active.value:
        raise HTTPException(status_code=400, detail="Deleted people cannot be invited")
    if not person.contact_email:
        raise HTTPException(status_code=400, detail="Person must have a contact email before inviting")
    if person.account_state == AccountState.suspended.value:
        raise HTTPException(status_code=400, detail="Suspended accounts cannot be invited")

    invite = await create_invite(db, person_id=person.id, created_by=current_user.id)
    if person.account_state != AccountState.active.value:
        person.account_state = AccountState.pending.value

    settings = get_settings()
    invite_url = f"{settings.BASE_URL.rstrip('/')}/invite/{invite.raw_token}"
    app_theme = get_runtime_theme_from_app(request.app)
    delivery = await send_invite_email(
        recipient_email=person.contact_email,
        recipient_name=person.display_name,
        invite_url=invite_url,
        invited_by_name=current_user.display_name,
        expires_at=invite.expires_at,
        family_name=app_theme.get("brand_display_name", "Family Book"),
    )

    invite.delivery_status = delivery.status
    invite.delivery_error = delivery.error
    invite.delivery_message_id = delivery.message_id
    if delivery.status == "sent":
        invite.sent_at = datetime.now(timezone.utc).isoformat()

    await log_audit(
        db,
        actor_id=current_user.id,
        action="create",
        entity_type="invite",
        entity_id=invite.id,
        new_value={
            "person_id": person.id,
            "delivery_status": delivery.status,
            "delivery_provider": delivery.provider,
        },
    )
    await db.commit()
    logger.info("Invite created for person %s by admin %s", person.id, current_user.id)

    return AdminInviteResponse(
        id=invite.id,
        person_id=person.id,
        contact_email=person.contact_email,
        invite_url=invite_url,
        claimed_at=None,
        revoked=invite.revoked,
        expires_at=invite.expires_at.isoformat(),
        delivery_status=delivery.status,
        delivery_provider=delivery.provider,
        delivery_message_id=delivery.message_id,
        delivery_error=delivery.error,
    )


@router.post("/api/admin/persons/{person_id}/magic-link", response_model=AdminMagicLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_person_magic_link(
    person_id: str,
    body: AdminMagicLinkRequest,
    request: Request,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    person = await db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if person.lifecycle_state != PersonLifecycleState.active.value:
        raise HTTPException(status_code=400, detail="Deleted people cannot receive sign-in links")
    if person.account_state != AccountState.active.value:
        raise HTTPException(status_code=400, detail="Only active accounts can receive sign-in links")
    if not person.contact_email:
        raise HTTPException(status_code=400, detail="Person must have a contact email before sending sign-in links")

    link_url, delivery = await _create_and_deliver_magic_link(
        db=db,
        person=person,
        request=request,
        return_to=body.return_to,
        send_email=body.send_email,
        actor_id=current_user.id,
        source="admin_support",
    )
    await db.commit()
    logger.info(
        "Admin %s created magic-link support credential for person %s",
        current_user.id,
        person.id,
    )
    return AdminMagicLinkResponse(
        person_id=person.id,
        contact_email=person.contact_email,
        magic_link_url=link_url,
        delivery_status=delivery.status,
        delivery_provider=delivery.provider,
        delivery_message_id=delivery.message_id,
        delivery_error=delivery.error,
    )


@router.post("/api/admin/invites/{invite_id}/revoke")
async def revoke_invite(
    invite_id: str,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    invite = await db.get(Invite, invite_id)
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    invite.revoked = True
    await log_audit(
        db,
        actor_id=current_user.id,
        action="delete",
        entity_type="invite",
        entity_id=invite.id,
        new_value={
            "person_id": invite.person_id,
            "credential_type": "invite",
        },
    )
    await db.commit()
    logger.info("Invite %s revoked by admin %s", invite.id, current_user.id)
    return {"status": "ok", "invite_id": invite.id}


@router.post("/api/admin/sessions/{session_id}/revoke")
async def revoke_session(
    session_id: str,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Revoke (delete) a single session by ID."""
    found = await delete_session_by_id(db, session_id)
    if not found:
        raise HTTPException(status_code=404, detail="Session not found")
    await log_audit(
        db,
        actor_id=current_user.id,
        action="delete",
        entity_type="session",
        entity_id=session_id,
        new_value={"scope": "single_session"},
    )
    await db.commit()
    logger.info("Session %s revoked by admin %s", session_id, current_user.id)
    return {"status": "ok", "session_id": session_id}


@router.post("/api/admin/persons/{person_id}/revoke-sessions")
async def revoke_all_sessions(
    person_id: str,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Revoke all sessions for a person."""
    person = await db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    count = await delete_all_sessions_for_person(db, person_id)
    await log_audit(
        db,
        actor_id=current_user.id,
        action="delete",
        entity_type="session",
        entity_id=person_id,
        new_value={
            "scope": "all_person_sessions",
            "revoked_count": count,
        },
    )
    await db.commit()
    logger.info(
        "All sessions (%d) for person %s revoked by admin %s",
        count, person_id, current_user.id,
    )
    return {"status": "ok", "person_id": person_id, "revoked_count": count}


@router.post("/api/admin/invites/{invite_id}/resend", response_model=AdminInviteResponse)
async def resend_invite(
    invite_id: str,
    request: Request,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    invite = await db.get(Invite, invite_id)
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    if invite.revoked:
        raise HTTPException(status_code=400, detail="Cannot resend a revoked invite")
    if invite.claimed_at is not None:
        raise HTTPException(status_code=400, detail="Invite has already been claimed")

    person = await db.get(Person, invite.person_id)
    if not person or not person.contact_email:
        raise HTTPException(status_code=400, detail="Person not found or missing contact email")

    settings = get_settings()
    # The raw token is not persisted, so we create a fresh invite for resend
    # and revoke the old one to maintain audit trail.
    new_invite = await create_invite(db, person_id=person.id, created_by=current_user.id)
    invite_url = f"{settings.BASE_URL.rstrip('/')}/invite/{new_invite.raw_token}"

    app_theme = get_runtime_theme_from_app(request.app)
    delivery = await send_invite_email(
        recipient_email=person.contact_email,
        recipient_name=person.display_name,
        invite_url=invite_url,
        invited_by_name=current_user.display_name,
        expires_at=new_invite.expires_at,
        family_name=app_theme.get("brand_display_name", "Family Book"),
    )

    new_invite.delivery_status = delivery.status
    new_invite.delivery_error = delivery.error
    new_invite.delivery_message_id = delivery.message_id
    if delivery.status == "sent":
        new_invite.sent_at = datetime.now(timezone.utc).isoformat()

    # Revoke the old invite since we issued a replacement
    invite.revoked = True

    await log_audit(
        db,
        actor_id=current_user.id,
        action="create",
        entity_type="invite",
        entity_id=new_invite.id,
        new_value={
            "person_id": person.id,
            "resent_from": invite_id,
            "delivery_status": delivery.status,
            "delivery_provider": delivery.provider,
        },
    )
    await db.commit()
    logger.info(
        "Invite %s resent as %s for person %s by admin %s",
        invite_id, new_invite.id, person.id, current_user.id,
    )

    return AdminInviteResponse(
        id=new_invite.id,
        person_id=person.id,
        contact_email=person.contact_email,
        invite_url=invite_url,
        claimed_at=None,
        revoked=new_invite.revoked,
        expires_at=new_invite.expires_at.isoformat(),
        delivery_status=delivery.status,
        delivery_provider=delivery.provider,
        delivery_message_id=delivery.message_id,
        delivery_error=delivery.error,
    )


@router.post("/api/admin/persons/{person_id}/approve")
async def approve_person(
    person_id: str,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    person = await db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if person.lifecycle_state != PersonLifecycleState.active.value:
        raise HTTPException(status_code=400, detail="Deleted people cannot be approved")
    person.account_state = AccountState.active.value
    await db.commit()
    logger.info("Person %s approved by admin %s", person.id, current_user.id)
    return {"status": "ok", "person_id": person.id}


@router.post("/api/admin/persons/{person_id}/suspend")
async def suspend_person(
    person_id: str,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    person = await db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if person.lifecycle_state != PersonLifecycleState.active.value:
        raise HTTPException(status_code=400, detail="Deleted people cannot be suspended")
    person.account_state = AccountState.suspended.value
    await db.commit()
    logger.info("Person %s suspended by admin %s", person.id, current_user.id)
    return {"status": "ok", "person_id": person.id}


@router.post("/api/admin/persons/{person_id}/activate")
async def activate_person(
    person_id: str,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    person = await db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if person.lifecycle_state != PersonLifecycleState.active.value:
        raise HTTPException(status_code=400, detail="Deleted people cannot be activated")
    person.account_state = AccountState.active.value
    await db.commit()
    logger.info("Person %s activated by admin %s", person.id, current_user.id)
    return {"status": "ok", "person_id": person.id}


@router.get("/api/admin/theme", response_model=ThemeSettingsPayload)
async def get_theme_settings(
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    settings_record = await get_or_create_theme_settings_record(db)
    return ThemeSettingsPayload(**settings_record.settings)


@router.put("/api/admin/theme", response_model=ThemeSettingsPayload)
async def update_theme_settings(
    body: ThemeSettingsPayload,
    request: Request,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    settings_record = await get_or_create_theme_settings_record(db)
    old_settings = settings_record.settings
    settings_record.settings = body.model_dump()
    await log_audit(
        db,
        actor_id=current_user.id,
        action="update",
        entity_type="app_theme",
        entity_id=settings_record.id,
        old_value=old_settings,
        new_value=settings_record.settings,
    )
    await sync_runtime_theme(request.app, db)
    logger.info("Theme settings updated by admin %s", current_user.id)
    return ThemeSettingsPayload(**settings_record.settings)


@router.post("/api/admin/theme/reset", response_model=ThemeSettingsPayload)
async def reset_theme_settings(
    request: Request,
    current_user: Person = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    settings_record = await get_or_create_theme_settings_record(db)
    old_settings = settings_record.settings
    settings_record.settings = DEFAULT_THEME_SETTINGS
    await log_audit(
        db,
        actor_id=current_user.id,
        action="reset",
        entity_type="app_theme",
        entity_id=settings_record.id,
        old_value=old_settings,
        new_value=settings_record.settings,
    )
    await sync_runtime_theme(request.app, db)
    logger.info("Theme settings reset by admin %s", current_user.id)
    return ThemeSettingsPayload(**settings_record.settings)


@router.post("/invite/{token}/claim")
async def claim_invite_route(
    token: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    person = await claim_invite(db, token)
    if not person:
        # Look up invite for a specific error message
        raw_invite = await get_invite_by_token(db, token)
        reason = get_invite_rejection_reason(raw_invite)
        error_messages = {
            "revoked": "This invite was cancelled.",
            "claimed": "This invite has already been used.",
            "expired": "This invite has expired. Ask your family admin for a new one.",
            "not_found": "Invite not found.",
        }
        raise HTTPException(
            status_code=400 if reason in ("revoked", "claimed", "expired") else 404,
            detail=error_messages.get(reason, "Invalid invite."),
        )
    session_token = await create_session(
        db,
        person_id=person.id,
        auth_method=AuthMethod.invite_code.value,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    person.last_login_at = datetime.now(timezone.utc).isoformat()
    await log_audit(
        db,
        actor_id=person.id,
        action="login",
        entity_type="session",
        entity_id=person.id,
        new_value={
            "auth_method": AuthMethod.invite_code.value,
            "ip": request.client.host if request.client else None,
        },
    )
    await log_audit(
        db,
        actor_id=person.id,
        action="claim",
        entity_type="invite_activation",
        entity_id=person.id,
        new_value={"role": get_person_role(person)},
    )
    await db.commit()
    _set_session_cookie(response, session_token)
    logger.info("Invite claimed for person %s", person.id)
    return {"status": "ok", "person_id": person.id, "landing_url": "/invite/first-steps"}
