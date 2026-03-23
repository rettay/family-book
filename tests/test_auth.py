import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.person import Person, AccountState
from app.models.auth import Invite, UserSession
from app.services.auth_service import (
    authenticate_google_identity,
    claim_invite,
    create_invite,
    create_session,
    validate_session,
    delete_session,
    _hash_token,
)


@pytest.mark.asyncio
async def test_create_and_validate_session(seeded_db: AsyncSession):
    token = await create_session(
        seeded_db,
        person_id="tyler-000-0000-0000-000000000002",
        auth_method="google_oauth",
    )
    await seeded_db.commit()

    person = await validate_session(seeded_db, token)
    assert person is not None
    assert person.first_name == "Tyler"


@pytest.mark.asyncio
async def test_invalid_session_returns_none(seeded_db: AsyncSession):
    person = await validate_session(seeded_db, "bogus-token")
    assert person is None


@pytest.mark.asyncio
async def test_delete_session(seeded_db: AsyncSession):
    token = await create_session(
        seeded_db,
        person_id="tyler-000-0000-0000-000000000002",
        auth_method="google_oauth",
    )
    await seeded_db.commit()

    await delete_session(seeded_db, token)
    await seeded_db.commit()

    person = await validate_session(seeded_db, token)
    assert person is None


@pytest.mark.asyncio
async def test_expired_session_rejected(seeded_db: AsyncSession):
    token = await create_session(
        seeded_db,
        person_id="tyler-000-0000-0000-000000000002",
        auth_method="google_oauth",
    )
    await seeded_db.commit()

    # Manually expire the session
    token_hash = _hash_token(token)
    result = await seeded_db.execute(
        select(UserSession).where(UserSession.token_hash == token_hash)
    )
    session = result.scalar_one()
    session.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    await seeded_db.commit()

    person = await validate_session(seeded_db, token)
    assert person is None


@pytest.mark.asyncio
async def test_suspended_user_session_rejected(seeded_db: AsyncSession):
    # Suspend Tyler
    result = await seeded_db.execute(
        select(Person).where(Person.id == "tyler-000-0000-0000-000000000002")
    )
    tyler = result.scalar_one()
    tyler.account_state = AccountState.suspended.value
    await seeded_db.commit()

    token = await create_session(
        seeded_db,
        person_id="tyler-000-0000-0000-000000000002",
        auth_method="google_oauth",
    )
    await seeded_db.commit()

    person = await validate_session(seeded_db, token)
    assert person is None


@pytest.mark.asyncio
async def test_authenticate_google_identity_links_by_email(seeded_db: AsyncSession):
    person = await authenticate_google_identity(
        seeded_db,
        google_sub="google-sub-1",
        email="tyler@example.com",
        email_verified=True,
    )
    await seeded_db.commit()

    assert person.first_name == "Tyler"
    refreshed = await seeded_db.get(Person, "tyler-000-0000-0000-000000000002")
    assert refreshed is not None
    assert refreshed.google_sub == "google-sub-1"
    assert refreshed.google_email == "tyler@example.com"


@pytest.mark.asyncio
async def test_authenticate_google_identity_uses_existing_google_sub(seeded_db: AsyncSession):
    person = await seeded_db.get(Person, "tyler-000-0000-0000-000000000002")
    assert person is not None
    person.google_sub = "google-sub-1"
    person.google_email = "tyler@example.com"
    await seeded_db.commit()

    resolved = await authenticate_google_identity(
        seeded_db,
        google_sub="google-sub-1",
        email="different@example.com",
        email_verified=True,
    )
    assert resolved.id == person.id


@pytest.mark.asyncio
async def test_authenticate_google_identity_requires_verified_email(seeded_db: AsyncSession):
    with pytest.raises(ValueError, match="not verified"):
        await authenticate_google_identity(
            seeded_db,
            google_sub="google-sub-1",
            email="tyler@example.com",
            email_verified=False,
        )


@pytest.mark.asyncio
async def test_authenticate_google_identity_rejects_unknown_email(seeded_db: AsyncSession):
    with pytest.raises(ValueError, match="No family profile matches"):
        await authenticate_google_identity(
            seeded_db,
            google_sub="google-sub-1",
            email="unknown@example.com",
            email_verified=True,
        )


@pytest.mark.asyncio
async def test_google_auth_immediately_authenticates_client(client: AsyncClient, monkeypatch):
    from app.routes import auth_routes

    monkeypatch.setattr(
        auth_routes,
        "verify_google_credential",
        lambda credential: {
            "sub": "google-sub-1",
            "email": "tyler@example.com",
            "email_verified": True,
        },
    )

    resp = await client.post("/auth/google", json={"credential": "test-credential"})
    assert resp.status_code == 200

    me = await client.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["display_name"] == "Tyler Martin"


@pytest.mark.asyncio
async def test_create_and_claim_invite_activates_person_and_creates_session(
    seeded_db: AsyncSession,
    client: AsyncClient,
):
    person = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    assert person is not None
    person.account_state = AccountState.pending.value
    person.contact_email = "jane@example.com"
    await seeded_db.commit()

    invite = await create_invite(
        seeded_db,
        person_id=person.id,
        created_by="tyler-000-0000-0000-000000000002",
    )
    await seeded_db.commit()

    claim_resp = await client.post(f"/invite/{invite.raw_token}/claim")
    assert claim_resp.status_code == 200
    assert "session=" in claim_resp.headers.get("set-cookie", "")

    await seeded_db.refresh(person)
    refreshed = await seeded_db.get(Person, person.id)
    assert refreshed is not None
    assert refreshed.account_state == AccountState.active.value


@pytest.mark.asyncio
async def test_admin_can_create_and_revoke_invite(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
):
    member = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    assert member is not None
    member.contact_email = "jane@example.com"
    await seeded_db.commit()

    create_resp = await admin_client.post(f"/api/admin/persons/{member.id}/invite")
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["person_id"] == member.id
    assert body["contact_email"] == "jane@example.com"
    assert "/invite/" in body["invite_url"]

    invite_result = await seeded_db.execute(select(Invite).where(Invite.person_id == member.id))
    invite = invite_result.scalar_one()

    revoke_resp = await admin_client.post(f"/api/admin/invites/{invite.id}/revoke")
    assert revoke_resp.status_code == 200

    await seeded_db.refresh(invite)
    refreshed = await seeded_db.get(Invite, invite.id)
    assert refreshed is not None
    assert refreshed.revoked is True


@pytest.mark.asyncio
async def test_admin_reinvite_does_not_downgrade_active_member(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
):
    member = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    assert member is not None
    member.contact_email = "jane@example.com"
    member.account_state = AccountState.active.value
    await seeded_db.commit()

    create_resp = await admin_client.post(f"/api/admin/persons/{member.id}/invite")
    assert create_resp.status_code == 201

    await seeded_db.refresh(member)
    refreshed = await seeded_db.get(Person, member.id)
    assert refreshed is not None
    assert refreshed.account_state == AccountState.active.value


@pytest.mark.asyncio
async def test_admin_can_suspend_and_activate_person(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
):
    member = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    assert member is not None

    suspend_resp = await admin_client.post(f"/api/admin/persons/{member.id}/suspend")
    assert suspend_resp.status_code == 200

    await seeded_db.refresh(member)
    suspended = await seeded_db.get(Person, member.id)
    assert suspended is not None
    assert suspended.account_state == AccountState.suspended.value

    activate_resp = await admin_client.post(f"/api/admin/persons/{member.id}/activate")
    assert activate_resp.status_code == 200

    await seeded_db.refresh(member)
    activated = await seeded_db.get(Person, member.id)
    assert activated is not None
    assert activated.account_state == AccountState.active.value
