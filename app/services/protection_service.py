from __future__ import annotations

import json
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.services.field_protection import (
    ENCRYPTED_PREFIX,
    PROTECTED_PERSON_FIELDS,
    contact_email_lookup_hash,
    decrypt_string,
    encrypt_mapping_fields,
    encrypt_string,
    get_fernet,
)

logger = logging.getLogger(__name__)


async def _protect_person_rows(session: AsyncSession) -> int:
    result = await session.execute(
        text(
            """
            SELECT
                id,
                medical_history,
                contact_whatsapp,
                contact_telegram,
                contact_signal,
                contact_email,
                contact_email_hash
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
    rows = result.mappings().all()
    for row in rows:
        contact_email = row["contact_email"]
        normalized_email = decrypt_string(contact_email) if contact_email else None
        await session.execute(
            text(
                """
                UPDATE persons
                SET
                    medical_history = :medical_history,
                    contact_whatsapp = :contact_whatsapp,
                    contact_telegram = :contact_telegram,
                    contact_signal = :contact_signal,
                    contact_email = :contact_email,
                    contact_email_hash = :contact_email_hash
                WHERE id = :id
                """
            ),
            {
                "id": row["id"],
                "medical_history": encrypt_string(row["medical_history"]),
                "contact_whatsapp": encrypt_string(row["contact_whatsapp"]),
                "contact_telegram": encrypt_string(row["contact_telegram"]),
                "contact_signal": encrypt_string(row["contact_signal"]),
                "contact_email": encrypt_string(contact_email),
                "contact_email_hash": contact_email_lookup_hash(normalized_email),
            },
        )
    return len(rows)


async def _protect_revision_rows(session: AsyncSession) -> int:
    result = await session.execute(
        text(
            """
            SELECT id, snapshot
            FROM entity_revisions
            WHERE entity_type = 'person'
            """
        )
    )
    revisions = result.mappings().all()
    protected_count = 0
    for row in revisions:
        snapshot = json.loads(row["snapshot"])
        protected_snapshot = encrypt_mapping_fields(snapshot, PROTECTED_PERSON_FIELDS)
        if protected_snapshot == snapshot:
            continue
        await session.execute(
            text("UPDATE entity_revisions SET snapshot = :snapshot WHERE id = :id"),
            {"id": row["id"], "snapshot": json.dumps(protected_snapshot)},
        )
        protected_count += 1
    return protected_count


async def _assert_readable_protected_data(session: AsyncSession) -> None:
    select_cols = ", ".join(PROTECTED_PERSON_FIELDS)
    where_clauses = " OR ".join(
        f"{f} LIKE 'enc::%'" for f in PROTECTED_PERSON_FIELDS
    )
    person_result = await session.execute(
        text(f"SELECT {select_cols} FROM persons WHERE {where_clauses} LIMIT 1")
    )
    person_row = person_result.mappings().first()
    if person_row:
        for field in PROTECTED_PERSON_FIELDS:
            value = person_row[field]
            if value and str(value).startswith(ENCRYPTED_PREFIX):
                decrypt_string(value)

    revision_result = await session.execute(
        text(
            """
            SELECT snapshot
            FROM entity_revisions
            WHERE entity_type = 'person' AND snapshot LIKE '%enc::%'
            LIMIT 5
            """
        )
    )
    for row in revision_result.mappings().all():
        snapshot = json.loads(row["snapshot"])
        for field in PROTECTED_PERSON_FIELDS:
            value = snapshot.get(field)
            if value and str(value).startswith(ENCRYPTED_PREFIX):
                decrypt_string(value)


async def ensure_sensitive_person_fields_protected(
    session_factory: async_sessionmaker | None = None,
) -> int:
    get_fernet()
    factory = session_factory or async_session_factory
    async with factory() as session:
        people_updated = await _protect_person_rows(session)
        revisions_updated = await _protect_revision_rows(session)
        await session.commit()
        await _assert_readable_protected_data(session)
        total_updated = people_updated + revisions_updated
        if total_updated:
            logger.info(
                "Protected %s person rows and %s revision rows",
                people_updated,
                revisions_updated,
            )
        return total_updated
