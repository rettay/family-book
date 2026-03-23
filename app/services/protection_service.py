from __future__ import annotations

import base64
import hashlib
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import get_settings
from app.database import async_session_factory

ENCRYPTED_PREFIX = "enc::"
PROTECTED_PERSON_FIELDS = [
    "medical_history",
    "contact_whatsapp",
    "contact_telegram",
    "contact_signal",
    "contact_email",
]


def normalize_email_for_lookup(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    return normalized or None


def contact_email_lookup_hash(value: str | None) -> str | None:
    normalized = normalize_email_for_lookup(value)
    if not normalized:
        return None
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _derive_fernet_key(raw_key: str) -> bytes:
    digest = hashlib.sha256(raw_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


@lru_cache(maxsize=8)
def _normalized_fernet_key(raw_key: str) -> bytes:
    candidate = raw_key.encode("utf-8")
    try:
        Fernet(candidate)
        return candidate
    except Exception:
        return _derive_fernet_key(raw_key)


def get_fernet() -> Fernet:
    settings = get_settings()
    return Fernet(_normalized_fernet_key(settings.FERNET_KEY))


def encrypt_string(value: str | None) -> str | None:
    if value is None:
        return None
    if value.startswith(ENCRYPTED_PREFIX):
        return value
    token = get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")
    return f"{ENCRYPTED_PREFIX}{token}"


def decrypt_string(value: str | None) -> str | None:
    if value is None:
        return None
    if not value.startswith(ENCRYPTED_PREFIX):
        return value
    token = value[len(ENCRYPTED_PREFIX):].encode("utf-8")
    try:
        return get_fernet().decrypt(token).decode("utf-8")
    except InvalidToken:
        return value


def encrypt_mapping_fields(snapshot: dict, fields: list[str]) -> dict:
    protected = dict(snapshot)
    for field in fields:
        if field in protected:
            protected[field] = encrypt_string(protected[field])
    return protected


def decrypt_mapping_fields(snapshot: dict, fields: list[str]) -> dict:
    unprotected = dict(snapshot)
    for field in fields:
        if field in unprotected:
            unprotected[field] = decrypt_string(unprotected[field])
    return unprotected


def get_protection_contract() -> dict:
    settings = get_settings()
    data_dir = getattr(settings, "resolved_data_dir", getattr(settings, "DATA_DIR", "data"))
    return {
        "field_encryption_enabled": True,
        "protected_person_fields": PROTECTED_PERSON_FIELDS,
        "transport_security": "HTTPS is required at deployment edge; cookies are marked secure when BASE_URL is https.",
        "storage_contract": (
            f"SQLite data, media, and backups are expected under {data_dir}. "
            "Field-level encryption protects direct-contact and medical fields in application storage."
        ),
        "notes": [
            "Field-level encryption is application-managed, not client-side end-to-end encryption.",
            "Backups preserve encrypted field values and must be protected as private family data.",
        ],
    }


async def ensure_sensitive_person_fields_protected(
    session_factory: async_sessionmaker | None = None,
) -> int:
    from app.models.person import Person

    factory = session_factory or async_session_factory
    async with factory() as session:
        result = await session.execute(
            text(
                """
                SELECT id
                FROM persons
                WHERE
                    (medical_history IS NOT NULL AND medical_history NOT LIKE 'enc::%')
                    OR (contact_whatsapp IS NOT NULL AND contact_whatsapp NOT LIKE 'enc::%')
                    OR (contact_telegram IS NOT NULL AND contact_telegram NOT LIKE 'enc::%')
                    OR (contact_signal IS NOT NULL AND contact_signal NOT LIKE 'enc::%')
                    OR (contact_email IS NOT NULL AND contact_email NOT LIKE 'enc::%')
                    OR (contact_email IS NOT NULL AND (contact_email_hash IS NULL OR contact_email_hash = ''))
                """
            )
        )
        person_ids = [row[0] for row in result.fetchall()]
        if not person_ids:
            return 0

        protected_count = 0
        for person_id in person_ids:
            person = await session.get(Person, person_id)
            if not person:
                continue
            for field in PROTECTED_PERSON_FIELDS:
                setattr(person, field, getattr(person, field))
            protected_count += 1

        await session.commit()
        return protected_count
