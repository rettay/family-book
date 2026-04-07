import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import UserSession, Invite, MagicLinkToken
from app.models.person import Person, AccountState, PersonLifecycleState
from app.config import get_settings
from app.services.field_protection import contact_email_lookup_hash, normalize_email_for_lookup

SESSION_TOKEN_BYTES = 32
SESSION_EXPIRY_DAYS = 30
MAX_SESSIONS_PER_PERSON = 10
MAGIC_LINK_EXPIRY_MINUTES = 15
INVITE_EXPIRY_DAYS = 30


def parse_user_agent_short(ua: str | None) -> str:
    """Extract browser and OS from user-agent string."""
    if not ua:
        return "Unknown"

    # Detect browser
    browser = "Unknown browser"
    if "Edg/" in ua or "Edge/" in ua:
        browser = "Edge"
    elif "OPR/" in ua or "Opera" in ua:
        browser = "Opera"
    elif "Chrome/" in ua and "Safari/" in ua:
        browser = "Chrome"
    elif "Firefox/" in ua:
        browser = "Firefox"
    elif "Safari/" in ua:
        browser = "Safari"

    # Detect OS
    os_name = "Unknown OS"
    if "iPhone" in ua or "iPad" in ua:
        os_name = "iOS"
    elif "Android" in ua:
        os_name = "Android"
    elif "Macintosh" in ua or "Mac OS" in ua:
        os_name = "macOS"
    elif "Windows" in ua:
        os_name = "Windows"
    elif "Linux" in ua:
        os_name = "Linux"

    return f"{browser} on {os_name}"


async def get_active_session_counts(db: AsyncSession) -> dict[str, int]:
    """Return a dict of person_id -> active (non-expired) session count."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(UserSession.person_id, func.count(UserSession.id))
        .where(UserSession.expires_at > now)
        .group_by(UserSession.person_id)
    )
    return {row[0]: row[1] for row in result.all()}


async def delete_all_sessions_for_person(db: AsyncSession, person_id: str) -> int:
    """Delete all sessions for a person. Returns count deleted."""
    result = await db.execute(
        delete(UserSession).where(UserSession.person_id == person_id)
    )
    return result.rowcount


async def delete_session_by_id(db: AsyncSession, session_id: str) -> bool:
    """Delete a session by its ID. Returns True if found and deleted."""
    session = await db.get(UserSession, session_id)
    if not session:
        return False
    await db.delete(session)
    return True


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def generate_session_token() -> str:
    return secrets.token_hex(SESSION_TOKEN_BYTES)


def generate_invite_token() -> str:
    return secrets.token_hex(32)


def generate_magic_link_token() -> str:
    return secrets.token_hex(32)


async def create_session(
    db: AsyncSession,
    person_id: str,
    auth_method: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> str:
    """Create a new session, returning the raw token (to be set as cookie)."""
    token = generate_session_token()
    token_hash = _hash_token(token)

    # Enforce max sessions per person — evict oldest
    result = await db.execute(
        select(UserSession)
        .where(UserSession.person_id == person_id)
        .order_by(UserSession.created_at.desc())
    )
    existing = result.scalars().all()
    if len(existing) >= MAX_SESSIONS_PER_PERSON:
        for old_session in existing[MAX_SESSIONS_PER_PERSON - 1:]:
            await db.delete(old_session)

    session = UserSession(
        person_id=person_id,
        token_hash=token_hash,
        auth_method=auth_method,
        expires_at=datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRY_DAYS),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(session)
    await db.flush()
    return token


async def validate_session(db: AsyncSession, token: str) -> Person | None:
    """Validate a session token, return the Person or None."""
    token_hash = _hash_token(token)
    result = await db.execute(
        select(UserSession).where(
            UserSession.token_hash == token_hash,
            UserSession.expires_at > datetime.now(timezone.utc),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        return None

    # Sliding expiry
    session.last_used = datetime.now(timezone.utc)
    session.expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRY_DAYS)

    result = await db.execute(
        select(Person).where(
            Person.id == session.person_id,
            Person.account_state == AccountState.active.value,
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
    )
    return result.scalar_one_or_none()


async def delete_session(db: AsyncSession, token: str) -> None:
    token_hash = _hash_token(token)
    await db.execute(
        delete(UserSession).where(UserSession.token_hash == token_hash)
    )


async def create_invite(
    db: AsyncSession,
    person_id: str,
    created_by: str,
) -> Invite:
    """Create an invite for a person. Returns the Invite with raw token on invite.raw_token."""
    token = generate_invite_token()
    token_hash = _hash_token(token)
    invite = Invite(
        person_id=person_id,
        token=token_hash,
        created_by=created_by,
        expires_at=datetime.now(timezone.utc) + timedelta(days=INVITE_EXPIRY_DAYS),
    )
    db.add(invite)
    await db.flush()
    invite.raw_token = token
    return invite


async def get_valid_invite(db: AsyncSession, token: str) -> Invite | None:
    token_hash = _hash_token(token)
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Invite).where(
            Invite.token == token_hash,
            Invite.claimed_at.is_(None),
            Invite.revoked.is_(False),
            Invite.expires_at > now,
        )
    )
    return result.scalar_one_or_none()


async def get_invite_by_token(db: AsyncSession, token: str) -> Invite | None:
    """Look up an invite by raw token regardless of status (for error messages)."""
    token_hash = _hash_token(token)
    result = await db.execute(
        select(Invite).where(Invite.token == token_hash)
    )
    return result.scalar_one_or_none()


async def claim_invite(db: AsyncSession, token: str) -> Person | None:
    """Claim an invite token. Returns the Person if valid, None otherwise."""
    invite = await get_valid_invite(db, token)
    if not invite:
        return None

    invite.claimed_at = datetime.now(timezone.utc)

    result = await db.execute(select(Person).where(Person.id == invite.person_id))
    person = result.scalar_one_or_none()
    if person:
        person.account_state = AccountState.active.value
    return person


def get_invite_rejection_reason(invite: Invite | None) -> str:
    """Return a specific rejection reason code for an invite that failed validation."""
    if invite is None:
        return "not_found"
    if invite.revoked:
        return "revoked"
    if invite.claimed_at is not None:
        return "claimed"
    now = datetime.now(timezone.utc)
    if invite.expires_at <= now:
        return "expired"
    return "not_found"


async def create_magic_link(db: AsyncSession, person_id: str) -> str:
    """Create a magic link token. Returns the raw token."""
    token = generate_magic_link_token()
    token_hash = _hash_token(token)
    ml = MagicLinkToken(
        person_id=person_id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=MAGIC_LINK_EXPIRY_MINUTES),
    )
    db.add(ml)
    await db.flush()
    return token


async def find_magic_link_person_by_email(db: AsyncSession, email: str | None) -> Person | None:
    """Return the active person for a normalized contact email, or None."""
    normalized_email = normalize_email_for_lookup(email)
    if not normalized_email:
        return None

    result = await db.execute(
        select(Person).where(
            Person.contact_email_hash == contact_email_lookup_hash(normalized_email),
            Person.account_state == AccountState.active.value,
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
    )
    matches = result.scalars().all()
    if len(matches) != 1:
        return None
    return matches[0]


async def validate_magic_link(db: AsyncSession, token: str) -> Person | None:
    """Validate and consume a magic link token. Returns Person if valid."""
    token_hash = _hash_token(token)
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(MagicLinkToken).where(
            MagicLinkToken.token_hash == token_hash,
            MagicLinkToken.used_at.is_(None),
            MagicLinkToken.expires_at > now,
        )
    )
    ml = result.scalar_one_or_none()
    if not ml:
        return None

    result = await db.execute(
        select(Person).where(
            Person.id == ml.person_id,
            Person.account_state == AccountState.active.value,
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
    )
    person = result.scalar_one_or_none()
    if not person:
        return None

    ml.used_at = now
    return person


async def get_magic_link_rejection_reason(db: AsyncSession, token: str) -> str:
    """Return a safe rejection reason for user-facing magic-link errors."""
    token_hash = _hash_token(token)
    result = await db.execute(
        select(MagicLinkToken).where(MagicLinkToken.token_hash == token_hash)
    )
    magic_link = result.scalar_one_or_none()
    if not magic_link:
        return "not_found"
    if magic_link.used_at is not None:
        return "used"
    now = datetime.now(timezone.utc)
    if _as_aware_utc(magic_link.expires_at) <= now:
        return "expired"
    result = await db.execute(
        select(Person).where(
            Person.id == magic_link.person_id,
            Person.account_state == AccountState.active.value,
            Person.lifecycle_state == PersonLifecycleState.active.value,
        )
    )
    if not result.scalar_one_or_none():
        return "unavailable"
    return "valid"


async def authenticate_google_identity(
    db: AsyncSession,
    *,
    google_sub: str,
    email: str | None,
    email_verified: bool,
) -> Person:
    if not email_verified:
        raise ValueError("Google account email is not verified.")

    normalized_email = normalize_email_for_lookup(email)
    settings = get_settings()

    result = await db.execute(
        select(Person).where(Person.google_sub == google_sub)
    )
    person = result.scalar_one_or_none()

    if person is None:
        if not normalized_email:
            raise ValueError("Google account is missing an email address.")

        result = await db.execute(
            select(Person).where(Person.contact_email_hash == contact_email_lookup_hash(normalized_email))
        )
        matches = result.scalars().all()

        if len(matches) != 1:
            raise ValueError(
                "No family profile matches this Google account email. "
                "Ask an admin to set your contact email first."
            )

        person = matches[0]
        person.google_sub = google_sub

    if person.account_state == AccountState.suspended.value:
        raise ValueError("This account is suspended.")

    if person.account_state == AccountState.pending.value:
        if settings.REQUIRE_APPROVAL:
            raise ValueError("This account is pending approval.")
        person.account_state = AccountState.active.value

    person.google_email = normalized_email
    return person
