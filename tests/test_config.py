from pathlib import Path

from app.config import Settings


def test_settings_admin_email_list_and_trusted_hosts():
    settings = Settings(
        SECRET_KEY="secret",
        FERNET_KEY="fernet",
        ADMIN_EMAILS=" Admin@Example.com, second@example.com ",
        BASE_URL="https://family.example.com",
        TRUSTED_HOSTS="cdn.example.com, family.example.com",
    )

    assert settings.admin_email_list == ["admin@example.com", "second@example.com"]
    assert settings.trusted_host_list == [
        "127.0.0.1",
        "cdn.example.com",
        "family.example.com",
        "localhost",
        "test",
    ]


def test_settings_sqlite_paths_resolve_data_dir(tmp_path):
    settings = Settings(
        SECRET_KEY="secret",
        FERNET_KEY="fernet",
        DATA_DIR=str(tmp_path / "family-data"),
        DATABASE_URL="sqlite:///data/family.db",
    )

    assert settings.sqlite_database_path == str((tmp_path / "family-data" / "family.db").resolve())
    assert settings.normalized_database_url == f"sqlite:///{settings.sqlite_database_path}"


def test_settings_non_sqlite_database_path_is_empty():
    settings = Settings(
        SECRET_KEY="secret",
        FERNET_KEY="fernet",
        DATABASE_URL="postgresql://db.example/family_book",
    )

    assert settings.sqlite_database_path == ""
    assert settings.normalized_database_url == "postgresql://db.example/family_book"


def test_settings_envelope_allowed_hosts_dedupes_and_infers_api_host():
    settings = Settings(
        SECRET_KEY="secret",
        FERNET_KEY="fernet",
        ENVELOPE_ALLOWED_HOSTS="Mail.EXAMPLE.com, mail.example.com, files.example.com",
        ENVELOPE_API_URL="https://mail.example.com/send",
    )

    assert settings.envelope_allowed_host_list == ["mail.example.com", "files.example.com"]


def test_settings_google_maps_and_resend_flags_require_full_config():
    settings = Settings(
        SECRET_KEY="secret",
        FERNET_KEY="fernet",
        GOOGLE_MAPS_API_KEY="maps-key",
        RESEND_API_KEY="resend-key",
        RESEND_FROM_EMAIL="Family Book <invites@example.com>",
    )

    assert settings.google_maps_enabled is True
    assert settings.resend_enabled is True

    incomplete = Settings(
        SECRET_KEY="secret",
        FERNET_KEY="fernet",
        RESEND_API_KEY="resend-key",
        RESEND_FROM_EMAIL="",
    )

    assert incomplete.google_maps_enabled is False
    assert incomplete.resend_enabled is False
