import sqlite3
from pathlib import Path

from alembic import command
from alembic.config import Config


ROOT_DIR = Path(__file__).resolve().parents[1]


def test_s48_privacy_role_migration_upgrades_existing_persons_table(monkeypatch, tmp_path):
    db_path = tmp_path / "pre_s48.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
    conn.execute("INSERT INTO alembic_version (version_num) VALUES ('fb107_passkeys')")
    conn.execute(
        """
        CREATE TABLE persons (
            id TEXT PRIMARY KEY,
            is_admin BOOLEAN NOT NULL DEFAULT 0
        )
        """
    )
    conn.execute("INSERT INTO persons (id, is_admin) VALUES ('admin-person', 1)")
    conn.execute("INSERT INTO persons (id, is_admin) VALUES ('member-person', 0)")
    conn.commit()
    conn.close()

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    config = Config(str(ROOT_DIR / "alembic.ini"))
    command.upgrade(config, "head")

    conn = sqlite3.connect(db_path)
    columns = {
        row[1]: row
        for row in conn.execute("PRAGMA table_info(persons)").fetchall()
    }
    rows = {
        row[0]: row[1:]
        for row in conn.execute(
            "SELECT id, role, contact_visibility, sensitive_visibility FROM persons"
        ).fetchall()
    }
    revision = conn.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    conn.close()

    assert "role" in columns
    assert "contact_visibility" in columns
    assert "sensitive_visibility" in columns
    assert rows["admin-person"] == ("admin", "close_family", "staff")
    assert rows["member-person"] == ("member", "close_family", "staff")
    assert revision == "b6c1d2e3f4a5"


def test_s50_onboarding_and_media_inbox_migration(monkeypatch, tmp_path):
    db_path = tmp_path / "pre_s50.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
    conn.execute("INSERT INTO alembic_version (version_num) VALUES ('f1a2b3c4d5e6')")
    conn.execute("CREATE TABLE persons (id TEXT PRIMARY KEY)")
    conn.execute("INSERT INTO persons (id) VALUES ('person-1')")
    conn.commit()
    conn.close()

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    config = Config(str(ROOT_DIR / "alembic.ini"))
    command.upgrade(config, "head")

    conn = sqlite3.connect(db_path)
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    revision = conn.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    conn.close()

    assert "onboarding_progress" in tables
    assert "media_inbox_items" in tables
    assert revision == "b6c1d2e3f4a5"


def test_s51_prompt_album_book_migration(monkeypatch, tmp_path):
    db_path = tmp_path / "pre_s51.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
    conn.execute("INSERT INTO alembic_version (version_num) VALUES ('a6d9f3b1c2e4')")
    conn.execute("CREATE TABLE persons (id TEXT PRIMARY KEY)")
    conn.execute("INSERT INTO persons (id) VALUES ('person-1')")
    conn.execute("CREATE TABLE media (id TEXT PRIMARY KEY)")
    conn.execute("INSERT INTO media (id) VALUES ('media-1')")
    conn.commit()
    conn.close()

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    config = Config(str(ROOT_DIR / "alembic.ini"))
    command.upgrade(config, "head")

    conn = sqlite3.connect(db_path)
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    revision = conn.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    conn.close()

    assert "prompt_campaigns" in tables
    assert "prompt_campaign_recipients" in tables
    assert "albums" in tables
    assert "album_media" in tables
    assert "book_projects" in tables
    assert revision == "b6c1d2e3f4a5"
