from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import get_settings
from app.database import async_session_factory
from app.models.person import AccountState, Person, PersonSource
from app.services.protection_service import contact_email_lookup_hash, normalize_email_for_lookup

logger = logging.getLogger(__name__)


async def ensure_bootstrap_admin(
    session_factory: async_sessionmaker | None = None,
) -> None:
    settings = get_settings()
    bootstrap_email = normalize_email_for_lookup(settings.BOOTSTRAP_ADMIN_EMAIL)
    if not bootstrap_email:
        return

    factory = session_factory or async_session_factory
    async with factory() as session:
        count_result = await session.execute(select(func.count()).select_from(Person))
        person_count = int(count_result.scalar() or 0)

        existing_result = await session.execute(
            select(Person).where(Person.contact_email_hash == contact_email_lookup_hash(bootstrap_email))
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            if not existing.is_admin or existing.account_state != AccountState.active.value:
                existing.is_admin = True
                existing.account_state = AccountState.active.value
                await session.commit()
                logger.info("Promoted bootstrap admin account for %s", bootstrap_email)
            return

        if person_count > 0:
            logger.warning(
                "Skipped bootstrap admin creation for %s because the database is not empty",
                bootstrap_email,
            )
            return

        person = Person(
            first_name=settings.BOOTSTRAP_ADMIN_FIRST_NAME.strip() or "Admin",
            last_name=settings.BOOTSTRAP_ADMIN_LAST_NAME.strip() or "User",
            contact_email=bootstrap_email,
            is_admin=True,
            is_root=False,
            source=PersonSource.manual.value,
            account_state=AccountState.active.value,
        )
        session.add(person)
        await session.commit()
        logger.info("Created bootstrap admin account for %s", bootstrap_email)
