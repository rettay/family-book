import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import SESSION_COOKIE_NAME, require_admin, require_auth
from app.config import get_settings
from app.database import get_db
from app.models.auth import AuthMethod, Invite
from app.models.person import AccountState, Person, PersonLifecycleState
from app.services.audit_service import log_audit
from app.services.google_auth import GoogleAuthError, verify_google_credential
from app.services.email_delivery import send_invite_email
from app.services.auth_service import (
    authenticate_google_identity,
    claim_invite,
    create_invite,
    create_session,
    delete_session,
)
from app.services.theme_service import (
    DEFAULT_THEME_SETTINGS,
    ThemeSettingsPayload,
    get_or_create_theme_settings_record,
    sync_runtime_theme,
)

router = APIRouter(tags=["auth"])
logger = logging.getLogger(__name__)


class GoogleCredentialRequest(BaseModel):
    credential: str


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
            Person.is_admin == True,
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
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    session_token = await create_session(
        db,
        person_id=person.id,
        auth_method=AuthMethod.google_oauth.value,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    await db.commit()

    _set_session_cookie(response, session_token)
    logger.info("Google authentication succeeded for person %s", person.id)
    return {"status": "ok", "person_id": person.id}


@router.post("/auth/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
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
        "is_admin": current_user.is_admin,
        "branch": current_user.branch,
    }


@router.post("/api/admin/persons/{person_id}/invite", response_model=AdminInviteResponse, status_code=status.HTTP_201_CREATED)
async def create_person_invite(
    person_id: str,
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
    await db.commit()
    logger.info("Invite created for person %s by admin %s", person.id, current_user.id)

    settings = get_settings()
    invite_url = f"{settings.BASE_URL.rstrip('/')}/invite/{invite.raw_token}"
    delivery = await send_invite_email(
        recipient_email=person.contact_email,
        recipient_name=person.display_name,
        invite_url=invite_url,
        invited_by_name=current_user.display_name,
        expires_at=invite.expires_at,
    )
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
    await db.commit()
    logger.info("Invite %s revoked by admin %s", invite.id, current_user.id)
    return {"status": "ok", "invite_id": invite.id}


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
        raise HTTPException(status_code=404, detail="Invite not found or already claimed")
    session_token = await create_session(
        db,
        person_id=person.id,
        auth_method=AuthMethod.invite_code.value,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    await db.commit()
    _set_session_cookie(response, session_token)
    logger.info("Invite claimed for person %s", person.id)
    return {"status": "ok", "person_id": person.id}
