import json

import pytest
from cryptography.fernet import Fernet
from sqlalchemy import text

from app.models.person import Person
from app.models.revisions import EntityRevision
from app.services.field_protection import (
    ProtectedFieldDecryptionError,
    ProtectionConfigurationError,
    _normalized_fernet_key,
    decrypt_string,
    encrypt_string,
    get_fernet,
    get_protection_contract,
)
from app.services.protection_service import ensure_sensitive_person_fields_protected


@pytest.fixture(autouse=True)
def clear_key_cache():
    _normalized_fernet_key.cache_clear()
    yield
    _normalized_fernet_key.cache_clear()


def test_invalid_fernet_key_is_rejected(monkeypatch):
    monkeypatch.setenv("FERNET_KEY", "test")

    with pytest.raises(ProtectionConfigurationError):
        get_fernet()


def test_decrypt_string_raises_for_wrong_key(monkeypatch):
    first_key = Fernet.generate_key().decode("utf-8")
    second_key = Fernet.generate_key().decode("utf-8")

    monkeypatch.setenv("FERNET_KEY", first_key)
    ciphertext = encrypt_string("sensitive note")

    monkeypatch.setenv("FERNET_KEY", second_key)

    with pytest.raises(ProtectedFieldDecryptionError):
        decrypt_string(ciphertext)


def test_protection_contract_reports_invalid_key(monkeypatch):
    monkeypatch.setenv("FERNET_KEY", "test")

    contract = get_protection_contract()

    assert contract["field_encryption_enabled"] is False
    assert contract["fernet_key_valid"] is False


@pytest.mark.asyncio
async def test_backfill_encrypts_legacy_person_revision_snapshots(session_factory):
    async with session_factory() as session:
        person = Person(first_name="Legacy", last_name="Relative")
        session.add(person)
        await session.flush()

        revision = EntityRevision(
            entity_type="person",
            entity_id=person.id,
            action="update",
        )
        revision.snapshot = {
            "first_name": "Legacy",
            "last_name": "Relative",
            "medical_history": "hypertension",
            "contact_email": "legacy@example.com",
        }
        session.add(revision)
        await session.commit()
        revision_id = revision.id

    updated = await ensure_sensitive_person_fields_protected(session_factory)

    assert updated >= 1

    async with session_factory() as session:
        raw_snapshot = (
            await session.execute(
                text("SELECT snapshot FROM entity_revisions WHERE id = :revision_id"),
                {"revision_id": revision_id},
            )
        ).scalar_one()

    assert "hypertension" not in raw_snapshot
    assert "legacy@example.com" not in raw_snapshot

    snapshot = json.loads(raw_snapshot)
    assert snapshot["medical_history"].startswith("enc::")
    assert snapshot["contact_email"].startswith("enc::")
