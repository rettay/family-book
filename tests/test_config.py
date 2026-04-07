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


def test_settings_google_maps_and_smtp_flags_require_full_config(monkeypatch):
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_MAPS_BROWSER_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_MAPS_SERVER_API_KEY", raising=False)
    settings = Settings(
        SECRET_KEY="secret",
        FERNET_KEY="fernet",
        GOOGLE_MAPS_BROWSER_API_KEY="maps-browser-key",
        GOOGLE_MAPS_SERVER_API_KEY="maps-server-key",
        SMTP_HOST="smtp.example.com",
        SMTP_USER="invites@example.com",
        SMTP_PASS="smtp-secret",
        SMTP_FROM="Family Book <invites@example.com>",
        _env_file=None,
    )

    assert settings.google_maps_enabled is True
    assert settings.google_places_enabled is True
    assert settings.google_geocoding_enabled is True
    assert settings.google_maps_browser_api_key_value == "maps-browser-key"
    assert settings.google_maps_server_api_key_value == "maps-server-key"
    assert settings.smtp_enabled is True
    assert settings.email_delivery_enabled is True

    incomplete = Settings(
        SECRET_KEY="secret",
        FERNET_KEY="fernet",
        SMTP_HOST="smtp.example.com",
        SMTP_USER="invites@example.com",
        SMTP_PASS="",
        SMTP_FROM="Family Book <invites@example.com>",
        _env_file=None,
    )

    assert incomplete.google_maps_enabled is False
    assert incomplete.google_places_enabled is False
    assert incomplete.google_geocoding_enabled is False
    assert incomplete.smtp_enabled is False
    assert incomplete.email_delivery_enabled is False


def test_settings_google_maps_placeholder_values_fail_closed(monkeypatch):
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    settings = Settings(
        SECRET_KEY="secret",
        FERNET_KEY="fernet",
        GOOGLE_MAPS_BROWSER_API_KEY="PENDING_SETUP",
        GOOGLE_MAPS_SERVER_API_KEY="TODO",
        GOOGLE_MAPS_MAP_ID="REPLACE_ME",
        _env_file=None,
    )

    assert settings.google_maps_enabled is False
    assert settings.google_geocoding_enabled is False
    assert settings.google_maps_browser_api_key_value == ""
    assert settings.google_maps_server_api_key_value == ""
    assert settings.google_maps_api_key_value == ""
    assert settings.google_maps_map_id_value == ""


def test_settings_google_maps_legacy_key_falls_back_for_browser_and_server(monkeypatch):
    monkeypatch.delenv("GOOGLE_MAPS_BROWSER_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_MAPS_SERVER_API_KEY", raising=False)
    settings = Settings(
        SECRET_KEY="secret",
        FERNET_KEY="fernet",
        GOOGLE_MAPS_API_KEY="legacy-key",
        _env_file=None,
    )

    assert settings.google_maps_enabled is True
    assert settings.google_places_enabled is True
    assert settings.google_geocoding_enabled is True
    assert settings.google_maps_browser_api_key_value == "legacy-key"
    assert settings.google_maps_server_api_key_value == "legacy-key"
    assert settings.google_maps_api_key_value == "legacy-key"
