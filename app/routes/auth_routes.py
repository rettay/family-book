from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import SESSION_COOKIE_NAME, require_admin, require_auth
from app.config import get_settings
from app.database import get_db
from app.models.auth import AuthMethod, Invite
from app.models.person import AccountState, Person
from app.services.google_auth import GoogleAuthError, verify_google_credential
from app.services.auth_service import (
    authenticate_google_identity,
    claim_invite,
    create_invite,
    create_session,
    delete_session,
)

router = APIRouter(tags=["auth"])


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
    if not person.contact_email:
        raise HTTPException(status_code=400, detail="Person must have a contact email before inviting")
    if person.account_state == AccountState.suspended.value:
        raise HTTPException(status_code=400, detail="Suspended accounts cannot be invited")

    invite = await create_invite(db, person_id=person.id, created_by=current_user.id)
    if person.account_state != AccountState.active.value:
        person.account_state = AccountState.pending.value
    await db.commit()

    settings = get_settings()
    return AdminInviteResponse(
        id=invite.id,
        person_id=person.id,
        contact_email=person.contact_email,
        invite_url=f"{settings.BASE_URL.rstrip('/')}/invite/{invite.raw_token}",
        claimed_at=None,
        revoked=invite.revoked,
        expires_at=invite.expires_at.isoformat(),
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
    person.account_state = AccountState.active.value
    await db.commit()
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
    person.account_state = AccountState.suspended.value
    await db.commit()
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
    person.account_state = AccountState.active.value
    await db.commit()
    return {"status": "ok", "person_id": person.id}


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
    return {"status": "ok", "person_id": person.id}
