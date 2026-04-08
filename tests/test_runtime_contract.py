from cryptography.fernet import Fernet

from app.config import Settings
from app.runtime_contract import production_runtime_enabled, validate_production_runtime


def _production_settings(tmp_path, **overrides):
    values = {
        "SECRET_KEY": "a" * 64,
        "FERNET_KEY": Fernet.generate_key().decode(),
        "BASE_URL": "https://family.example.com",
        "DATA_DIR": str(tmp_path),
        "DATABASE_URL": "sqlite:///data/family.db",
        "DEV_BYPASS_AUTH": False,
        "ENABLE_API_DOCS": False,
        "_env_file": None,
    }
    values.update(overrides)
    return Settings(**values)


def test_production_runtime_enabled_from_known_markers():
    assert production_runtime_enabled({"FAMILY_BOOK_ENV": "production"}) is True
    assert production_runtime_enabled({"APP_ENV": "production"}) is True
    assert production_runtime_enabled({"ENVIRONMENT": "production"}) is True
    assert production_runtime_enabled({"RAILWAY_ENVIRONMENT_NAME": "production"}) is True
    assert production_runtime_enabled({"FAMILY_BOOK_ENV": "staging"}) is False


def test_validate_production_runtime_accepts_safe_single_tenant_defaults(tmp_path):
    settings = _production_settings(tmp_path)

    assert validate_production_runtime(settings, {"LOAD_DEMO_DATA": "false"}) == []


def test_validate_production_runtime_rejects_dev_bypass_demo_seed_and_bad_secrets(tmp_path):
    settings = _production_settings(
        tmp_path,
        SECRET_KEY="test",
        FERNET_KEY="test",
        BASE_URL="http://family.example.com",
        DEV_BYPASS_AUTH=True,
        ENABLE_API_DOCS=True,
    )

    errors = validate_production_runtime(settings, {"LOAD_DEMO_DATA": "comprehensive"})

    assert "SECRET_KEY must be a generated 64-character hex value." in errors
    assert "FERNET_KEY must be a valid Fernet key." in errors
    assert "BASE_URL must use https:// in production." in errors
    assert "DEV_BYPASS_AUTH must be false in production." in errors
    assert "ENABLE_API_DOCS must be false in production." in errors
    assert "LOAD_DEMO_DATA must be false or unset in production." in errors


def test_validate_production_runtime_rejects_sqlite_outside_data_dir(tmp_path):
    settings = _production_settings(
        tmp_path / "data",
        DATABASE_URL=f"sqlite:///{tmp_path / 'elsewhere' / 'family.db'}",
    )

    assert "SQLite DATABASE_URL must point inside DATA_DIR in production." in (
        validate_production_runtime(settings)
    )


def test_validate_production_runtime_rejects_non_sqlite_database_urls(tmp_path):
    settings = _production_settings(
        tmp_path,
        DATABASE_URL="postgresql://db.example/family_book",
    )

    assert (
        "Production DATABASE_URL must use sqlite:/// and point to a database inside DATA_DIR."
        in validate_production_runtime(settings)
    )
