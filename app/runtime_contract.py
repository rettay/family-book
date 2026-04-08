from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Mapping

from app.config import Settings, get_settings
from app.services.field_protection import is_valid_fernet_key

_PLACEHOLDER_VALUES = {"", "PENDING_SETUP", "REPLACE_ME", "TODO", "CHANGE_ME"}


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _is_placeholder(value: str | None) -> bool:
    cleaned = _clean(value)
    return not cleaned or cleaned.upper() in _PLACEHOLDER_VALUES


def production_runtime_enabled(environ: Mapping[str, str] | None = None) -> bool:
    env = environ or os.environ
    markers = (
        env.get("FAMILY_BOOK_ENV"),
        env.get("APP_ENV"),
        env.get("ENVIRONMENT"),
        env.get("RAILWAY_ENVIRONMENT_NAME"),
    )
    return any(_clean(marker).lower() == "production" for marker in markers)


def validate_production_runtime(
    settings: Settings | None = None,
    environ: Mapping[str, str] | None = None,
) -> list[str]:
    settings = settings or get_settings()
    env = environ or os.environ
    errors: list[str] = []

    secret_key = _clean(settings.SECRET_KEY)
    if _is_placeholder(secret_key) or not re.fullmatch(r"[0-9a-fA-F]{64}", secret_key):
        errors.append("SECRET_KEY must be a generated 64-character hex value.")

    if _is_placeholder(settings.FERNET_KEY) or not is_valid_fernet_key(settings.FERNET_KEY):
        errors.append("FERNET_KEY must be a valid Fernet key.")

    if not settings.BASE_URL.startswith("https://"):
        errors.append("BASE_URL must use https:// in production.")

    if settings.DEV_BYPASS_AUTH:
        errors.append("DEV_BYPASS_AUTH must be false in production.")

    if settings.ENABLE_API_DOCS:
        errors.append("ENABLE_API_DOCS must be false in production.")

    load_demo_data = _clean(env.get("LOAD_DEMO_DATA")).lower()
    if load_demo_data not in {"", "false", "0", "no"}:
        errors.append("LOAD_DEMO_DATA must be false or unset in production.")

    data_dir = Path(settings.resolved_data_dir)
    if not data_dir.is_absolute():
        errors.append("DATA_DIR must resolve to an absolute persistent volume path.")

    if not settings.DATABASE_URL.startswith("sqlite:///"):
        errors.append(
            "Production DATABASE_URL must use sqlite:/// and point to a database inside DATA_DIR."
        )
        return errors

    db_path = Path(settings.sqlite_database_path).resolve()
    try:
        db_path.relative_to(data_dir.resolve())
    except ValueError:
        errors.append("SQLite DATABASE_URL must point inside DATA_DIR in production.")

    return errors


def assert_production_runtime() -> None:
    if not production_runtime_enabled():
        return

    errors = validate_production_runtime()
    if errors:
        details = "\n".join(f"- {error}" for error in errors)
        raise RuntimeError(f"Production runtime contract failed:\n{details}")


if __name__ == "__main__":
    assert_production_runtime()
