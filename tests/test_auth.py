import pytest
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.routes.auth_routes as auth_routes
from app.models.person import Person, AccountState, PersonLifecycleState
from app.models.audit import AuditLog
from app.models.auth import Invite, MagicLinkToken, PasskeyChallenge, PasskeyCredential, UserSession
from app.services.auth_service import (
    authenticate_google_identity,
    create_invite,
    create_magic_link,
    create_session,
    validate_session,
    delete_session,
    _hash_token,
)
from app.services.email_delivery import InviteDeliveryResult


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
    assert body["delivery_status"] == "not_configured"
    assert body["delivery_provider"] is None

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
async def test_admin_invite_reports_smtp_delivery_result(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
):
    member = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    assert member is not None
    member.contact_email = "jane@example.com"
    await seeded_db.commit()

    async def fake_send_invite_email(**kwargs):
        assert kwargs["recipient_email"] == "jane@example.com"
        assert "/invite/" in kwargs["invite_url"]
        return InviteDeliveryResult(
            status="sent",
            provider="smtp",
            message_id="smtp_123",
        )

    monkeypatch.setattr(auth_routes, "send_invite_email", fake_send_invite_email)

    create_resp = await admin_client.post(f"/api/admin/persons/{member.id}/invite")
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["delivery_status"] == "sent"
    assert body["delivery_provider"] == "smtp"
    assert body["delivery_message_id"] == "smtp_123"


@pytest.mark.asyncio
async def test_admin_invite_preserves_link_when_delivery_fails(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
):
    member = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    assert member is not None
    member.contact_email = "jane@example.com"
    await seeded_db.commit()

    async def fake_send_invite_email(**kwargs):
        return InviteDeliveryResult(
            status="failed",
            provider="smtp",
            error="temporary outage",
        )

    monkeypatch.setattr(auth_routes, "send_invite_email", fake_send_invite_email)

    create_resp = await admin_client.post(f"/api/admin/persons/{member.id}/invite")
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["delivery_status"] == "failed"
    assert body["delivery_error"] == "temporary outage"
    assert "/invite/" in body["invite_url"]


@pytest.mark.asyncio
async def test_magic_link_request_is_generic_and_sends_for_active_person(
    client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
):
    sent = {}

    async def fake_send_magic_link_email(**kwargs):
        sent.update(kwargs)
        return InviteDeliveryResult(status="sent", provider="smtp", message_id="smtp_ml_1")

    monkeypatch.setattr(auth_routes, "send_magic_link_email", fake_send_magic_link_email)

    known_resp = await client.post(
        "/auth/magic-link/request",
        json={"email": "tyler@example.com", "return_to": "/tree"},
    )
    unknown_resp = await client.post(
        "/auth/magic-link/request",
        json={"email": "unknown@example.com", "return_to": "/tree"},
    )

    assert known_resp.status_code == 200
    assert unknown_resp.status_code == 200
    assert known_resp.json()["message"] == unknown_resp.json()["message"]
    assert sent["recipient_email"] == "tyler@example.com"
    assert "/auth/magic-link/" in sent["magic_link_url"]

    tokens = (
        await seeded_db.execute(
            select(MagicLinkToken).where(
                MagicLinkToken.person_id == "tyler-000-0000-0000-000000000002"
            )
        )
    ).scalars().all()
    assert len(tokens) == 1
    assert len(tokens[0].token_hash) == 64
    assert sent["magic_link_url"].rsplit("/", 1)[-1].split("?", 1)[0] != tokens[0].token_hash


@pytest.mark.asyncio
async def test_magic_link_request_throttle_uses_request_key_without_enumeration(
    client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
):
    tyler = await seeded_db.get(Person, "tyler-000-0000-0000-000000000002")
    assert tyler is not None
    tyler.contact_email = "throttle-known@example.com"
    await seeded_db.commit()

    async def fake_send_magic_link_email(**kwargs):
        return InviteDeliveryResult(status="sent", provider="smtp", message_id="smtp_ml_throttle")

    monkeypatch.setattr(auth_routes, "send_magic_link_email", fake_send_magic_link_email)

    known_responses = [
        await client.post(
            "/auth/magic-link/request",
            json={"email": "throttle-known@example.com"},
        )
        for _ in range(auth_routes.MAGIC_LINK_REQUEST_LIMIT + 1)
    ]
    unknown_responses = [
        await client.post(
            "/auth/magic-link/request",
            json={"email": "throttle-unknown@example.com"},
        )
        for _ in range(auth_routes.MAGIC_LINK_REQUEST_LIMIT + 1)
    ]

    assert [resp.status_code for resp in known_responses] == [200, 200, 200, 429]
    assert [resp.status_code for resp in unknown_responses] == [200, 200, 200, 429]
    assert known_responses[-1].json() == unknown_responses[-1].json()


@pytest.mark.asyncio
async def test_magic_link_claim_creates_session_and_is_single_use(
    client: AsyncClient,
    seeded_db: AsyncSession,
):
    raw_token = await create_magic_link(
        seeded_db,
        person_id="tyler-000-0000-0000-000000000002",
    )
    await seeded_db.commit()

    claim_resp = await client.post(f"/auth/magic-link/{raw_token}/claim?return_to=/tree")
    assert claim_resp.status_code == 200
    assert claim_resp.json()["return_to"] == "/tree"
    assert "session=" in claim_resp.headers.get("set-cookie", "")

    replay_resp = await client.post(f"/auth/magic-link/{raw_token}/claim")
    assert replay_resp.status_code == 400

    sessions = (
        await seeded_db.execute(
            select(UserSession).where(
                UserSession.person_id == "tyler-000-0000-0000-000000000002",
                UserSession.auth_method == "magic_link",
            )
        )
    ).scalars().all()
    assert len(sessions) == 1


@pytest.mark.asyncio
async def test_magic_link_expired_token_fails_without_session(
    client: AsyncClient,
    seeded_db: AsyncSession,
):
    raw_token = await create_magic_link(
        seeded_db,
        person_id="tyler-000-0000-0000-000000000002",
    )
    token_hash = _hash_token(raw_token)
    result = await seeded_db.execute(
        select(MagicLinkToken).where(MagicLinkToken.token_hash == token_hash)
    )
    magic_link = result.scalar_one()
    magic_link.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    await seeded_db.commit()

    claim_resp = await client.post(f"/auth/magic-link/{raw_token}/claim")

    assert claim_resp.status_code == 400
    failed_audit = (
        await seeded_db.execute(
            select(AuditLog).where(
                AuditLog.action == "login_failed",
                AuditLog.entity_type == "magic_link",
            )
        )
    ).scalar_one()
    assert failed_audit.new_value["reason"] == "expired"
    assert raw_token not in (failed_audit._new_value or "")


@pytest.mark.asyncio
async def test_admin_can_create_copy_only_magic_link(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
):
    member = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    assert member is not None
    member.contact_email = "jane@example.com"
    member.account_state = AccountState.active.value
    await seeded_db.commit()

    resp = await admin_client.post(
        f"/api/admin/persons/{member.id}/magic-link",
        json={"send_email": False},
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["delivery_status"] == "manual"
    assert body["delivery_provider"] is None
    assert "/auth/magic-link/" in body["magic_link_url"]

    audit = (
        await seeded_db.execute(
            select(AuditLog).where(
                AuditLog.entity_type == "magic_link",
                AuditLog.entity_id == member.id,
            )
        )
    ).scalar_one()
    assert audit.new_value["source"] == "admin_support"
    assert body["magic_link_url"].rsplit("/", 1)[-1] not in (audit._new_value or "")


@pytest.mark.asyncio
async def test_passkey_registration_stores_public_credential(
    member_client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
):
    options_resp = await member_client.post("/auth/passkeys/register/options")
    assert options_resp.status_code == 200
    challenge_id = options_resp.json()["challenge_id"]

    def fake_verify_registration_response(**kwargs):
        assert kwargs["expected_rp_id"] == "localhost"
        assert kwargs["expected_origin"] == "http://localhost:8000"
        return SimpleNamespace(
            credential_id=b"credential-1",
            credential_public_key=b"public-key-only",
            sign_count=7,
            credential_device_type=SimpleNamespace(value="multi_device"),
            credential_backed_up=True,
        )

    monkeypatch.setattr(
        auth_routes,
        "verify_registration_response",
        fake_verify_registration_response,
    )

    verify_resp = await member_client.post(
        "/auth/passkeys/register/verify",
        json={
            "challenge_id": challenge_id,
            "credential": {"id": "credential-1"},
            "label": "Jane's iPad",
        },
    )

    assert verify_resp.status_code == 200
    body = verify_resp.json()
    assert body["label"] == "Jane's iPad"

    credential = (
        await seeded_db.execute(select(PasskeyCredential))
    ).scalar_one()
    assert credential.credential_id == "Y3JlZGVudGlhbC0x"
    assert credential.public_key == "cHVibGljLWtleS1vbmx5"
    assert credential.sign_count == 7
    assert credential.backed_up is True

    challenge = await seeded_db.get(PasskeyChallenge, challenge_id)
    assert challenge is not None
    assert challenge.used_at is not None


@pytest.mark.asyncio
async def test_passkey_registration_failure_consumes_challenge_and_audits(
    member_client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
):
    options_resp = await member_client.post("/auth/passkeys/register/options")
    assert options_resp.status_code == 200
    challenge_id = options_resp.json()["challenge_id"]

    def fake_verify_registration_response(**kwargs):
        raise auth_routes.InvalidRegistrationResponse("bad attestation")

    monkeypatch.setattr(
        auth_routes,
        "verify_registration_response",
        fake_verify_registration_response,
    )

    verify_resp = await member_client.post(
        "/auth/passkeys/register/verify",
        json={
            "challenge_id": challenge_id,
            "credential": {"id": "credential-1"},
        },
    )

    assert verify_resp.status_code == 400
    challenge = await seeded_db.get(PasskeyChallenge, challenge_id)
    assert challenge is not None
    assert challenge.used_at is not None

    audit = (
        await seeded_db.execute(
            select(AuditLog).where(
                AuditLog.action == "register_failed",
                AuditLog.entity_type == "passkey",
            )
        )
    ).scalar_one()
    assert audit.new_value["reason"].startswith("invalid_response")
    assert audit.new_value["challenge_id"] == challenge_id


@pytest.mark.asyncio
async def test_passkey_authentication_creates_session_and_blocks_replay(
    client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
):
    credential = PasskeyCredential(
        person_id="tyler-000-0000-0000-000000000002",
        credential_id="Y3JlZGVudGlhbC0x",
        public_key="cHVibGljLWtleS1vbmx5",
        sign_count=1,
        label="Tyler passkey",
    )
    seeded_db.add(credential)
    await seeded_db.commit()

    options_resp = await client.post("/auth/passkeys/authenticate/options")
    assert options_resp.status_code == 200
    challenge_id = options_resp.json()["challenge_id"]

    def fake_verify_authentication_response(**kwargs):
        assert kwargs["credential_current_sign_count"] == 1
        return SimpleNamespace(
            new_sign_count=2,
            credential_backed_up=False,
        )

    monkeypatch.setattr(
        auth_routes,
        "verify_authentication_response",
        fake_verify_authentication_response,
    )

    auth_resp = await client.post(
        "/auth/passkeys/authenticate/verify",
        json={
            "challenge_id": challenge_id,
            "credential": {"id": "Y3JlZGVudGlhbC0x"},
            "return_to": "/tree",
        },
    )
    assert auth_resp.status_code == 200
    assert "session=" in auth_resp.headers.get("set-cookie", "")

    replay_resp = await client.post(
        "/auth/passkeys/authenticate/verify",
        json={
            "challenge_id": challenge_id,
            "credential": {"id": "Y3JlZGVudGlhbC0x"},
        },
    )
    assert replay_resp.status_code == 400

    refreshed = await seeded_db.get(PasskeyCredential, credential.id)
    assert refreshed is not None
    await seeded_db.refresh(refreshed)
    assert refreshed.sign_count == 2
    assert refreshed.last_used_at is not None


@pytest.mark.asyncio
async def test_passkey_authentication_unknown_credential_consumes_challenge_and_audits(
    client: AsyncClient,
    seeded_db: AsyncSession,
):
    options_resp = await client.post("/auth/passkeys/authenticate/options")
    assert options_resp.status_code == 200
    challenge_id = options_resp.json()["challenge_id"]

    resp = await client.post(
        "/auth/passkeys/authenticate/verify",
        json={
            "challenge_id": challenge_id,
            "credential": {"id": "unknown-passkey"},
        },
    )

    assert resp.status_code == 400
    challenge = await seeded_db.get(PasskeyChallenge, challenge_id)
    assert challenge is not None
    assert challenge.used_at is not None

    audit = (
        await seeded_db.execute(
            select(AuditLog).where(
                AuditLog.action == "login_failed",
                AuditLog.entity_type == "passkey",
                AuditLog.entity_id == challenge_id,
            )
        )
    ).scalar_one()
    assert audit.new_value["reason"] == "unknown_credential"


@pytest.mark.asyncio
async def test_passkey_authentication_suspended_account_consumes_challenge_and_audits(
    client: AsyncClient,
    seeded_db: AsyncSession,
):
    tyler = await seeded_db.get(Person, "tyler-000-0000-0000-000000000002")
    assert tyler is not None
    tyler.account_state = AccountState.suspended.value
    credential = PasskeyCredential(
        person_id=tyler.id,
        credential_id="c3VzcGVuZGVkLWNyZWRlbnRpYWw",
        public_key="cHVibGljLWtleS1vbmx5",
        sign_count=1,
        label="Suspended passkey",
    )
    seeded_db.add(credential)
    await seeded_db.commit()

    options_resp = await client.post("/auth/passkeys/authenticate/options")
    assert options_resp.status_code == 200
    challenge_id = options_resp.json()["challenge_id"]

    resp = await client.post(
        "/auth/passkeys/authenticate/verify",
        json={
            "challenge_id": challenge_id,
            "credential": {"id": "c3VzcGVuZGVkLWNyZWRlbnRpYWw"},
        },
    )

    assert resp.status_code == 403
    challenge = await seeded_db.get(PasskeyChallenge, challenge_id)
    assert challenge is not None
    assert challenge.used_at is not None

    audit = (
        await seeded_db.execute(
            select(AuditLog).where(
                AuditLog.action == "login_failed",
                AuditLog.entity_type == "passkey",
                AuditLog.entity_id == credential.id,
            )
        )
    ).scalar_one()
    assert audit.new_value["reason"] == "account_unavailable"
    assert audit.new_value["person_id"] == tyler.id


@pytest.mark.asyncio
async def test_passkey_authentication_invalid_response_consumes_challenge_and_audits(
    client: AsyncClient,
    seeded_db: AsyncSession,
    monkeypatch,
):
    credential = PasskeyCredential(
        person_id="tyler-000-0000-0000-000000000002",
        credential_id="aW52YWxpZC1yZXNwb25zZS1jcmVkZW50aWFs",
        public_key="cHVibGljLWtleS1vbmx5",
        sign_count=1,
        label="Tyler passkey",
    )
    seeded_db.add(credential)
    await seeded_db.commit()

    options_resp = await client.post("/auth/passkeys/authenticate/options")
    assert options_resp.status_code == 200
    challenge_id = options_resp.json()["challenge_id"]

    def fake_verify_authentication_response(**kwargs):
        raise auth_routes.InvalidAuthenticationResponse("bad assertion")

    monkeypatch.setattr(
        auth_routes,
        "verify_authentication_response",
        fake_verify_authentication_response,
    )

    resp = await client.post(
        "/auth/passkeys/authenticate/verify",
        json={
            "challenge_id": challenge_id,
            "credential": {"id": "aW52YWxpZC1yZXNwb25zZS1jcmVkZW50aWFs"},
        },
    )

    assert resp.status_code == 400
    challenge = await seeded_db.get(PasskeyChallenge, challenge_id)
    assert challenge is not None
    assert challenge.used_at is not None

    audit = (
        await seeded_db.execute(
            select(AuditLog).where(
                AuditLog.action == "login_failed",
                AuditLog.entity_type == "passkey",
                AuditLog.entity_id == credential.id,
            )
        )
    ).scalar_one()
    assert audit.new_value["reason"].startswith("invalid_response")
    assert audit.new_value["challenge_id"] == challenge_id


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


@pytest.mark.asyncio
async def test_deleted_person_cannot_be_invited_or_state_toggled(
    admin_client: AsyncClient,
    seeded_db: AsyncSession,
):
    member = await seeded_db.get(Person, "member-00-0000-0000-000000000005")
    assert member is not None
    member.contact_email = "jane@example.com"
    member.lifecycle_state = PersonLifecycleState.deleted.value
    await seeded_db.commit()

    invite_resp = await admin_client.post(f"/api/admin/persons/{member.id}/invite")
    assert invite_resp.status_code == 400

    approve_resp = await admin_client.post(f"/api/admin/persons/{member.id}/approve")
    assert approve_resp.status_code == 400

    suspend_resp = await admin_client.post(f"/api/admin/persons/{member.id}/suspend")
    assert suspend_resp.status_code == 400

    activate_resp = await admin_client.post(f"/api/admin/persons/{member.id}/activate")
    assert activate_resp.status_code == 400
