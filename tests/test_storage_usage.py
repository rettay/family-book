from pathlib import Path

from app.services.storage_usage_service import compute_archive_storage_usage


def test_compute_archive_storage_usage_counts_database_media_variants_backups_and_exports(
    monkeypatch,
    tmp_path,
):
    data_dir = tmp_path / "data"
    media_root = data_dir / "media"
    (media_root / "originals").mkdir(parents=True)
    (media_root / "variants" / "media-1").mkdir(parents=True)
    (media_root / "thumbnails").mkdir(parents=True)
    (data_dir / "backups").mkdir(parents=True)
    (data_dir / "exports").mkdir(parents=True)

    db_path = data_dir / "family.db"
    db_path.write_bytes(b"d" * 11)
    (media_root / "originals" / "photo.jpg").write_bytes(b"o" * 101)
    (media_root / "variants" / "media-1" / "thumb.jpg").write_bytes(b"v" * 21)
    (media_root / "thumbnails" / "legacy.jpg").write_bytes(b"t" * 13)
    (data_dir / "backups" / "backup.zip").write_bytes(b"b" * 31)
    (data_dir / "exports" / "export.zip").write_bytes(b"e" * 17)

    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    usage = compute_archive_storage_usage(str(data_dir))

    assert usage.database_bytes == 11
    assert usage.media_originals_bytes == 101
    assert usage.media_variants_bytes == 34
    assert usage.backups_bytes == 31
    assert usage.exports_bytes == 17
    assert usage.total_bytes == 194
