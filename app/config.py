from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Required
    SECRET_KEY: str
    FERNET_KEY: str
    BASE_URL: str = "http://localhost:8000"
    STAGING_REVIEW_URL: str = ""
    ENABLE_API_DOCS: bool = False
    DEV_BYPASS_AUTH: bool = False
    TRUSTED_HOSTS: str = ""

    # Database
    DATABASE_URL: str = "sqlite:///data/family.db"
    DATA_DIR: str = os.environ.get("RAILWAY_VOLUME_MOUNT_PATH", "data")
    BACKUP_RETENTION_DAYS: int = 30

    # Facebook OAuth
    FB_ENABLED: bool = False
    FB_APP_ID: str = ""
    FB_APP_SECRET: str = ""

    # Google Sign-In
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_HOSTED_DOMAIN: str = ""
    GOOGLE_MAPS_BROWSER_API_KEY: str = ""
    GOOGLE_MAPS_SERVER_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""
    GOOGLE_MAPS_MAP_ID: str = ""

    # Admin
    ADMIN_EMAILS: str = ""
    REQUIRE_APPROVAL: bool = False
    BOOTSTRAP_ADMIN_EMAIL: str = ""
    BOOTSTRAP_ADMIN_FIRST_NAME: str = "Admin"
    BOOTSTRAP_ADMIN_LAST_NAME: str = "User"

    # SMTP for invite and magic-link delivery
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_FROM: str = ""

    # Hosted archive / operator platform
    HOSTED_ARCHIVE_ENABLED: bool = False
    HOSTED_ARCHIVE_KEY: str = ""
    HOSTED_ARCHIVE_NAME: str = "Family Book Hosted Archive"
    HOSTED_ARCHIVE_OWNER_EMAIL: str = ""
    HOSTED_ARCHIVE_PLAN: str = "founding"
    HOSTED_ARCHIVE_BILLING_PROVIDER: str = "stripe"
    HOSTED_ARCHIVE_STORAGE_QUOTA_BYTES: int = 0
    OPERATOR_TOKENS: str = ""

    # Stripe hosted billing
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_FOUNDING: str = ""
    STRIPE_PRICE_FAMILY: str = ""
    STRIPE_PRICE_FAMILY_PLUS: str = ""

    # Passkeys / WebAuthn
    PASSKEY_RP_ID: str = ""
    PASSKEY_RP_NAME: str = "Family Book"

    # Inbound Envelope webhook
    ENVELOPE_API_URL: str = ""
    ENVELOPE_API_KEY: str = ""
    ENVELOPE_WEBHOOK_SECRET: str = ""
    ENVELOPE_ALLOWED_HOSTS: str = ""
    ENVELOPE_MAX_ATTACHMENT_BYTES: int = 25 * 1024 * 1024

    # Matrix
    MATRIX_HOMESERVER: str = ""
    MATRIX_BOT_USER: str = ""
    MATRIX_BOT_PASSWORD: str = ""
    MATRIX_FAMILY_ROOM: str = ""

    # External record search API keys
    TROVE_API_KEY: str = ""
    DPLA_API_KEY: str = ""
    FAMILYSEARCH_APP_KEY: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000
    FAMILY_GRAPH_MAX_DISTANCE: int = 4
    PERSON_CONTACT_MAX_DISTANCE: int = 1

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @staticmethod
    def _normalized_secret(value: str) -> str:
        cleaned = value.strip()
        if cleaned.upper() in {"PENDING_SETUP", "REPLACE_ME", "TODO"}:
            return ""
        return cleaned

    @property
    def admin_email_list(self) -> list[str]:
        if not self.ADMIN_EMAILS:
            return []
        return [e.strip().lower() for e in self.ADMIN_EMAILS.split(",") if e.strip()]

    @property
    def resolved_data_dir(self) -> str:
        return str(Path(self.DATA_DIR).expanduser().resolve())

    @property
    def normalized_database_url(self) -> str:
        if not self.DATABASE_URL.startswith("sqlite:///"):
            return self.DATABASE_URL
        return f"sqlite:///{self.sqlite_database_path}"

    @property
    def sqlite_database_path(self) -> str:
        if not self.DATABASE_URL.startswith("sqlite:///"):
            return ""

        raw_path = self.DATABASE_URL.replace("sqlite:///", "", 1)
        db_path = Path(raw_path)
        if db_path.is_absolute():
            return str(db_path)

        if db_path.parts and db_path.parts[0] == "data":
            db_path = Path(self.resolved_data_dir).joinpath(*db_path.parts[1:])
        else:
            db_path = (Path.cwd() / db_path).resolve()

        return str(db_path)

    @property
    def trusted_host_list(self) -> list[str]:
        hosts = {"localhost", "127.0.0.1", "test"}
        base_host = urlparse(self.BASE_URL).hostname
        if base_host:
            hosts.add(base_host)
        if self.TRUSTED_HOSTS:
            hosts.update(host.strip() for host in self.TRUSTED_HOSTS.split(",") if host.strip())
        return sorted(hosts)

    @property
    def envelope_allowed_host_list(self) -> list[str]:
        hosts = []
        if self.ENVELOPE_ALLOWED_HOSTS:
            hosts.extend(
                host.strip().lower()
                for host in self.ENVELOPE_ALLOWED_HOSTS.split(",")
                if host.strip()
            )

        api_host = urlparse(self.ENVELOPE_API_URL).hostname
        if api_host:
            hosts.append(api_host.lower())

        deduped: list[str] = []
        for host in hosts:
            if host not in deduped:
                deduped.append(host)
        return deduped

    @property
    def google_maps_enabled(self) -> bool:
        return bool(self.google_maps_browser_api_key_value)

    @property
    def google_places_enabled(self) -> bool:
        return self.google_maps_enabled

    @property
    def google_geocoding_enabled(self) -> bool:
        return bool(self.google_maps_server_api_key_value)

    @property
    def google_maps_browser_api_key_value(self) -> str:
        return self._normalized_secret(
            self.GOOGLE_MAPS_BROWSER_API_KEY or self.GOOGLE_MAPS_API_KEY
        )

    @property
    def google_maps_server_api_key_value(self) -> str:
        return self._normalized_secret(
            self.GOOGLE_MAPS_SERVER_API_KEY or self.GOOGLE_MAPS_API_KEY
        )

    @property
    def google_maps_api_key_value(self) -> str:
        """Legacy alias for older template/runtime call sites."""
        return self.google_maps_browser_api_key_value

    @property
    def google_maps_map_id_value(self) -> str:
        return self._normalized_secret(self.GOOGLE_MAPS_MAP_ID)

    @property
    def smtp_enabled(self) -> bool:
        return bool(
            self.SMTP_HOST.strip()
            and self.SMTP_USER.strip()
            and self.SMTP_PASS.strip()
            and self.SMTP_FROM.strip()
        )

    @property
    def hosted_archive_enabled(self) -> bool:
        return bool(self.HOSTED_ARCHIVE_ENABLED)

    @property
    def operator_token_list(self) -> list[str]:
        return [
            token.strip()
            for token in self.OPERATOR_TOKENS.split(",")
            if token.strip()
        ]

    @property
    def stripe_secret_key_value(self) -> str:
        return self._normalized_secret(self.STRIPE_SECRET_KEY)

    @property
    def stripe_webhook_secret_value(self) -> str:
        return self._normalized_secret(self.STRIPE_WEBHOOK_SECRET)

    @property
    def stripe_price_map(self) -> dict[str, str]:
        mapping = {
            "founding": self._normalized_secret(self.STRIPE_PRICE_FOUNDING),
            "family": self._normalized_secret(self.STRIPE_PRICE_FAMILY),
            "family_plus": self._normalized_secret(self.STRIPE_PRICE_FAMILY_PLUS),
        }
        return {plan_code: price_id for plan_code, price_id in mapping.items() if price_id}

    @property
    def stripe_enabled(self) -> bool:
        return bool(
            self.hosted_archive_enabled
            and self.HOSTED_ARCHIVE_BILLING_PROVIDER.strip().lower() == "stripe"
            and self.stripe_secret_key_value
            and self.stripe_webhook_secret_value
        )

    @property
    def email_delivery_enabled(self) -> bool:
        return self.smtp_enabled

    @property
    def passkey_rp_id(self) -> str:
        configured = self.PASSKEY_RP_ID.strip()
        if configured:
            return configured
        base_host = urlparse(self.BASE_URL).hostname
        return base_host or "localhost"

    @property
    def passkey_origin(self) -> str:
        parsed = urlparse(self.BASE_URL)
        if not parsed.scheme or not parsed.netloc:
            return self.BASE_URL.rstrip("/")
        return f"{parsed.scheme}://{parsed.netloc}"


def get_settings() -> Settings:
    return Settings()
