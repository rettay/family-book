from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.config import get_settings


@dataclass(frozen=True)
class ArchiveStorageUsage:
    database_bytes: int
    media_originals_bytes: int
    media_variants_bytes: int
    backups_bytes: int
    exports_bytes: int

    @property
    def total_bytes(self) -> int:
        return (
            self.database_bytes
            + self.media_originals_bytes
            + self.media_variants_bytes
            + self.backups_bytes
            + self.exports_bytes
        )


def _safe_file_size(path: Path) -> int:
    if not path.exists() or not path.is_file():
        return 0
    return path.stat().st_size


def _walk_file_sizes(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def compute_archive_storage_usage(data_dir: str | None = None) -> ArchiveStorageUsage:
    settings = get_settings()
    resolved_data_dir = Path(data_dir or settings.resolved_data_dir)
    database_path = Path(settings.sqlite_database_path) if settings.sqlite_database_path else None
    media_root = resolved_data_dir / "media"

    media_variants_root = media_root / "variants"
    media_thumbnails_root = media_root / "thumbnails"
    media_variants_bytes = _walk_file_sizes(media_variants_root) + _walk_file_sizes(media_thumbnails_root)
    media_originals_bytes = _walk_file_sizes(media_root) - media_variants_bytes
    if media_originals_bytes < 0:
        media_originals_bytes = 0

    return ArchiveStorageUsage(
        database_bytes=_safe_file_size(database_path) if database_path else 0,
        media_originals_bytes=media_originals_bytes,
        media_variants_bytes=media_variants_bytes,
        backups_bytes=_walk_file_sizes(resolved_data_dir / "backups"),
        exports_bytes=_walk_file_sizes(resolved_data_dir / "exports"),
    )


def format_bytes(num_bytes: int | None) -> str:
    if num_bytes is None:
        return "Unlimited"
    value = float(num_bytes)
    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{int(num_bytes)} B"
