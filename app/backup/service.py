"""
Backup service — SQLite .backup API + media directory, retention, health check.
"""

import gzip
import json
import logging
import os
import shutil
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from app.config import get_settings
from app.services.field_protection import get_protection_contract

logger = logging.getLogger(__name__)


def _backup_dir(settings) -> str:
    data_dir = getattr(settings, "resolved_data_dir", settings.DATA_DIR)
    return os.path.join(data_dir, "backups")


def _restore_verification_path(backup_dir: str) -> Path:
    return Path(backup_dir) / "restore-verification.json"


def _load_restore_verification(backup_dir: str) -> dict | None:
    path = _restore_verification_path(backup_dir)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.warning("Restore verification metadata is unreadable: %s", path)
        return None


def _write_restore_verification(backup_dir: str, payload: dict) -> None:
    path = _restore_verification_path(backup_dir)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _latest_backup(backup_dir: str) -> Path | None:
    backups = sorted(Path(backup_dir).glob("family-*.db.gz"), reverse=True)
    return backups[0] if backups else None


def _restore_supported(latest_backup: Path | None, verification: dict | None) -> bool:
    if not latest_backup or not verification:
        return False
    return (
        verification.get("status") == "ok"
        and verification.get("source_backup") == latest_backup.name
    )


def _safe_extract_archive(zf: zipfile.ZipFile, destination: Path) -> None:
    destination = destination.resolve()
    for member in zf.infolist():
        member_name = member.filename
        if not member_name or member_name.endswith("/"):
            continue

        target_path = (destination / member_name).resolve()
        try:
            target_path.relative_to(destination)
        except ValueError as exc:
            raise ValueError(f"Backup archive contains an unsafe path: {member_name}") from exc

        target_path.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(member) as src, open(target_path, "wb") as dst:
            shutil.copyfileobj(src, dst)

def run_backup() -> str:
    """Run a SQLite backup + compress. Returns backup file path."""
    settings = get_settings()
    data_dir = getattr(settings, "resolved_data_dir", settings.DATA_DIR)
    backup_dir = _backup_dir(settings)
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_name = f"family-{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_name)
    gz_path = f"{backup_path}.gz"

    # Use SQLite's backup API (safe for WAL mode)
    db_path = getattr(
        settings,
        "sqlite_database_path",
        settings.DATABASE_URL.replace("sqlite:///", "", 1),
    )

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}")

    src = sqlite3.connect(db_path)
    dst = sqlite3.connect(backup_path)
    src.backup(dst)
    dst.close()
    src.close()

    # Compress
    with open(backup_path, "rb") as f_in:
        with gzip.open(gz_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(backup_path)

    logger.info("Backup created: %s", gz_path)
    _cleanup_old_backups(backup_dir, getattr(settings, "BACKUP_RETENTION_DAYS", 30))
    return gz_path


def create_download_zip() -> str:
    """Create a .zip containing latest backup + media directory. Returns zip path."""
    settings = get_settings()
    data_dir = getattr(settings, "resolved_data_dir", settings.DATA_DIR)
    backup_dir = _backup_dir(settings)

    # Find latest backup
    backups = sorted(Path(backup_dir).glob("family-*.db.gz"), reverse=True)
    if not backups:
        # Run a fresh backup
        run_backup()
        backups = sorted(Path(backup_dir).glob("family-*.db.gz"), reverse=True)

    zip_path = os.path.join(backup_dir, "family-book-backup.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add latest DB backup
        if backups:
            zf.write(str(backups[0]), f"db/{backups[0].name}")

        # Add media files
        media_dir = os.path.join(data_dir, "media")
        if os.path.isdir(media_dir):
            for root, _dirs, files in os.walk(media_dir):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    arcname = os.path.relpath(fpath, data_dir)
                    zf.write(fpath, arcname)

    return zip_path


def get_backup_health() -> dict:
    """Return backup freshness info for health check."""
    settings = get_settings()
    data_dir = getattr(settings, "resolved_data_dir", settings.DATA_DIR)
    backup_dir = _backup_dir(settings)
    latest = _latest_backup(backup_dir)
    verification = _load_restore_verification(backup_dir)
    database_path = getattr(
        settings,
        "sqlite_database_path",
        settings.DATABASE_URL.replace("sqlite:///", "", 1),
    )

    if not latest:
        return {
            "last_backup": None,
            "backup_count": 0,
            "fresh": False,
            "data_dir": data_dir,
            "database_path": database_path,
            "retention_days": getattr(settings, "BACKUP_RETENTION_DAYS", 30),
            "restore_supported": False,
            "restore_verification": verification,
            "protection": get_protection_contract(),
        }

    mtime = datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
    age_hours = (datetime.now(timezone.utc) - mtime).total_seconds() / 3600
    backups = sorted(Path(backup_dir).glob("family-*.db.gz"), reverse=True)

    return {
        "last_backup": mtime.isoformat(),
        "backup_count": len(backups),
        "fresh": age_hours < 25,  # less than 25 hours old
        "latest_file": latest.name,
        "latest_size_bytes": latest.stat().st_size,
        "data_dir": data_dir,
        "database_path": database_path,
        "retention_days": getattr(settings, "BACKUP_RETENTION_DAYS", 30),
        "restore_supported": _restore_supported(latest, verification),
        "restore_verification": verification,
        "protection": get_protection_contract(),
    }


def restore_backup_archive(
    archive_path: str,
    *,
    target_data_dir: str,
    target_db_filename: str | None = None,
) -> dict:
    target_root = Path(target_data_dir)
    target_root.mkdir(parents=True, exist_ok=True)
    media_target = target_root / "media"
    media_target.mkdir(parents=True, exist_ok=True)

    db_filename = target_db_filename or "family.db"
    db_target = target_root / db_filename

    with tempfile.TemporaryDirectory(prefix="family-book-restore-") as tmp_dir:
        tmp_root = Path(tmp_dir)
        with zipfile.ZipFile(archive_path, "r") as zf:
            _safe_extract_archive(zf, tmp_root)

        backup_candidates = sorted((tmp_root / "db").glob("*.db.gz"))
        if not backup_candidates:
            raise FileNotFoundError("Backup archive does not contain a database payload")

        with gzip.open(backup_candidates[0], "rb") as f_in, open(db_target, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

        extracted_media = tmp_root / "media"
        restored_media_files = 0
        if extracted_media.is_dir():
            for source in extracted_media.rglob("*"):
                if not source.is_file():
                    continue
                rel_path = source.relative_to(extracted_media)
                destination = media_target / rel_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                restored_media_files += 1

    with sqlite3.connect(str(db_target)) as restored_db:
        table_count = restored_db.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
        try:
            person_count = restored_db.execute("SELECT COUNT(*) FROM persons").fetchone()[0]
        except sqlite3.DatabaseError:
            person_count = None

    return {
        "restored_db_path": str(db_target),
        "restored_media_files": restored_media_files,
        "table_count": table_count,
        "person_count": person_count,
    }


def verify_backup_restore() -> dict:
    settings = get_settings()
    backup_dir = _backup_dir(settings)
    archive_path = create_download_zip()
    latest_backup = _latest_backup(backup_dir)
    db_filename = Path(
        getattr(
            settings,
            "sqlite_database_path",
            settings.DATABASE_URL.replace("sqlite:///", "", 1),
        )
    ).name or "family.db"

    try:
        with tempfile.TemporaryDirectory(prefix="family-book-restore-check-") as tmp_dir:
            restored = restore_backup_archive(
                archive_path,
                target_data_dir=tmp_dir,
                target_db_filename=db_filename,
            )
        verification = {
            "status": "ok",
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "archive_path": archive_path,
            "db_filename": db_filename,
            "source_backup": latest_backup.name if latest_backup else None,
            "table_count": restored["table_count"],
            "person_count": restored["person_count"],
            "restored_media_files": restored["restored_media_files"],
        }
        _write_restore_verification(backup_dir, verification)
        return verification
    except Exception as exc:
        failure = {
            "status": "error",
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "archive_path": archive_path,
            "db_filename": db_filename,
            "source_backup": latest_backup.name if latest_backup else None,
            "error": str(exc),
        }
        _write_restore_verification(backup_dir, failure)
        raise


def _cleanup_old_backups(backup_dir: str, retention_days: int) -> None:
    """Remove backups older than retention period."""
    now = datetime.now(timezone.utc)
    for f in Path(backup_dir).glob("family-*.db.gz"):
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        age_days = (now - mtime).days
        if age_days > retention_days:
            f.unlink()
            logger.info("Removed old backup: %s (%d days old)", f.name, age_days)
