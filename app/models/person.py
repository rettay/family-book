import enum
import json

from sqlalchemy import Boolean, Float, Index, LargeBinary, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy.types import TypeDecorator

from app.models.base import Base, TimestampMixin, generate_uuid
from app.services.field_protection import (
    contact_email_lookup_hash,
    decrypt_string,
    encrypt_string,
    normalize_email_for_lookup,
)


class EncryptedText(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return encrypt_string(value)

    def process_result_value(self, value, dialect):
        return decrypt_string(value)


class NameDisplayOrder(str, enum.Enum):
    western = "western"
    eastern = "eastern"
    patronymic = "patronymic"


class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class DatePrecision(str, enum.Enum):
    exact = "exact"
    month = "month"
    year = "year"
    decade = "decade"
    approximate = "approximate"


class Visibility(str, enum.Enum):
    visible = "visible"
    hidden = "hidden"
    memorial = "memorial"


class AccountState(str, enum.Enum):
    active = "active"
    pending = "pending"
    suspended = "suspended"


class PersonRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    steward = "steward"
    member = "member"
    viewer = "viewer"


class PersonLifecycleState(str, enum.Enum):
    active = "active"
    deleted = "deleted"


class PersonSource(str, enum.Enum):
    manual = "manual"
    facebook_oauth = "facebook_oauth"
    gedcom_import = "gedcom_import"
    whatsapp_import = "whatsapp_import"
    messenger_import = "messenger_import"
    federation = "federation"
    matrix = "matrix"


class ContactVisibility(str, enum.Enum):
    close_family = "close_family"
    staff = "staff"
    private = "private"


class SensitiveVisibility(str, enum.Enum):
    self = "self"
    staff = "staff"
    close_family = "close_family"


class Person(Base, TimestampMixin):
    __tablename__ = "persons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    first_name: Mapped[str] = mapped_column(String(200))
    last_name: Mapped[str] = mapped_column(String(200))
    patronymic: Mapped[str | None] = mapped_column(String(200), default=None)
    birth_last_name: Mapped[str | None] = mapped_column(String(200), default=None)
    nickname: Mapped[str | None] = mapped_column(String(100), default=None)
    _alternate_nicknames: Mapped[str | None] = mapped_column("alternate_nicknames", Text, default="[]")
    name_display_order: Mapped[str] = mapped_column(
        String(20), default=NameDisplayOrder.western.value
    )
    gender: Mapped[str | None] = mapped_column(String(10), default=None)

    birth_date_raw: Mapped[str | None] = mapped_column(String(50), default=None)
    birth_date: Mapped[str | None] = mapped_column(String(10), default=None)  # ISO 8601
    birth_date_precision: Mapped[str | None] = mapped_column(String(20), default=None)
    death_date_raw: Mapped[str | None] = mapped_column(String(50), default=None)
    death_date: Mapped[str | None] = mapped_column(String(10), default=None)
    death_date_precision: Mapped[str | None] = mapped_column(String(20), default=None)
    is_living: Mapped[bool] = mapped_column(Boolean, default=True)

    birth_place: Mapped[str | None] = mapped_column(String(300), default=None)
    birth_country_code: Mapped[str | None] = mapped_column(String(2), default=None)
    birth_place_latitude: Mapped[float | None] = mapped_column(Float, default=None)
    birth_place_longitude: Mapped[float | None] = mapped_column(Float, default=None)
    residence_place: Mapped[str | None] = mapped_column(String(300), default=None)
    residence_country_code: Mapped[str | None] = mapped_column(String(2), default=None)
    residence_place_latitude: Mapped[float | None] = mapped_column(Float, default=None)
    residence_place_longitude: Mapped[float | None] = mapped_column(Float, default=None)
    burial_place: Mapped[str | None] = mapped_column(String(300), default=None)
    burial_country_code: Mapped[str | None] = mapped_column(String(2), default=None)
    burial_place_latitude: Mapped[float | None] = mapped_column(Float, default=None)
    burial_place_longitude: Mapped[float | None] = mapped_column(Float, default=None)
    burial_cemetery_name: Mapped[str | None] = mapped_column(String(300), default=None)
    burial_plot_number: Mapped[str | None] = mapped_column(String(100), default=None)
    remains_disposition: Mapped[str | None] = mapped_column(String(20), default=None)

    _languages: Mapped[str | None] = mapped_column("languages", Text, default="[]")
    bio: Mapped[str | None] = mapped_column(String(2000), default=None)
    research_notes: Mapped[str | None] = mapped_column(Text, default=None)
    medical_history: Mapped[str | None] = mapped_column(EncryptedText(), default=None)

    obituary: Mapped[str | None] = mapped_column(Text, default=None)
    obituary_source: Mapped[str | None] = mapped_column(String(500), default=None)
    obituary_url: Mapped[str | None] = mapped_column(String(1000), default=None)
    _education: Mapped[str | None] = mapped_column("education", Text, default="[]")
    _career: Mapped[str | None] = mapped_column("career", Text, default="[]")
    _organizations: Mapped[str | None] = mapped_column("organizations", Text, default="[]")

    # Physical attributes (NOT encrypted)
    height: Mapped[str | None] = mapped_column(String(50), default=None)
    weight: Mapped[str | None] = mapped_column(String(50), default=None)
    eye_color: Mapped[str | None] = mapped_column(String(50), default=None)
    hair_color: Mapped[str | None] = mapped_column(String(50), default=None)
    blood_type: Mapped[str | None] = mapped_column(String(10), default=None)

    # Genetic profile (encrypted at rest)
    maternal_haplogroup: Mapped[str | None] = mapped_column(EncryptedText(), default=None)
    paternal_haplogroup: Mapped[str | None] = mapped_column(EncryptedText(), default=None)
    dna_test_provider: Mapped[str | None] = mapped_column(EncryptedText(), default=None)
    _admixture: Mapped[str | None] = mapped_column("admixture", EncryptedText(), default="[]")

    # Structured medical conditions (encrypted at rest)
    _medical_conditions: Mapped[str | None] = mapped_column("medical_conditions", EncryptedText(), default="[]")

    # Source citations (NOT encrypted — research data)
    source_detail: Mapped[str | None] = mapped_column(String(500), default=None)
    confidence: Mapped[str | None] = mapped_column(String(20), default=None)

    # Social profile URLs (public, not encrypted)
    social_instagram: Mapped[str | None] = mapped_column(String(300), default=None)
    social_facebook: Mapped[str | None] = mapped_column(String(300), default=None)
    social_twitter: Mapped[str | None] = mapped_column(String(300), default=None)
    social_linkedin: Mapped[str | None] = mapped_column(String(300), default=None)
    social_tiktok: Mapped[str | None] = mapped_column(String(300), default=None)
    social_youtube: Mapped[str | None] = mapped_column(String(300), default=None)

    # Multi-value social accounts (public, not encrypted) — replaces individual social_* columns
    _social_accounts: Mapped[str | None] = mapped_column("social_accounts", Text, default="[]")

    # Name history (encrypted — contains identity data)
    _name_history: Mapped[str | None] = mapped_column("name_history", EncryptedText(), default="[]")

    # Place history timeline (not encrypted — location data)
    _place_history: Mapped[str | None] = mapped_column("place_history", Text, default="[]")

    # Wiki slug (URL-safe, generated once on create)
    slug: Mapped[str | None] = mapped_column(String(200), unique=True, default=None, index=True)

    contact_whatsapp: Mapped[str | None] = mapped_column(EncryptedText(), default=None)
    contact_telegram: Mapped[str | None] = mapped_column(EncryptedText(), default=None)
    contact_signal: Mapped[str | None] = mapped_column(EncryptedText(), default=None)
    contact_phone: Mapped[str | None] = mapped_column(EncryptedText(), default=None)
    contact_email: Mapped[str | None] = mapped_column(EncryptedText(), default=None)
    _contact_addresses: Mapped[str | None] = mapped_column("contact_addresses", EncryptedText(), default="[]")
    _contact_phones: Mapped[str | None] = mapped_column("contact_phones", EncryptedText(), default="[]")
    _contact_emails: Mapped[str | None] = mapped_column("contact_emails", EncryptedText(), default="[]")
    contact_email_hash: Mapped[str | None] = mapped_column(String(64), default=None)
    calendar_feed_token: Mapped[str] = mapped_column(String(36), unique=True, default=generate_uuid)

    photo_url: Mapped[str | None] = mapped_column(String(2000), default=None)
    branch: Mapped[str | None] = mapped_column(String(100), default=None)

    is_root: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String(20), default=PersonRole.member.value)
    visibility: Mapped[str] = mapped_column(String(20), default=Visibility.visible.value)
    contact_visibility: Mapped[str] = mapped_column(
        String(20), default=ContactVisibility.close_family.value
    )
    sensitive_visibility: Mapped[str] = mapped_column(
        String(20), default=SensitiveVisibility.staff.value
    )
    account_state: Mapped[str] = mapped_column(String(20), default=AccountState.active.value)
    lifecycle_state: Mapped[str] = mapped_column(
        String(20), default=PersonLifecycleState.active.value
    )
    deleted_at: Mapped[str | None] = mapped_column(String(40), default=None)
    deleted_by: Mapped[str | None] = mapped_column(String(36), default=None)
    last_login_at: Mapped[str | None] = mapped_column(String(40), default=None)

    google_sub: Mapped[str | None] = mapped_column(String(255), unique=True, default=None)
    google_email: Mapped[str | None] = mapped_column(String(320), default=None)
    facebook_id: Mapped[str | None] = mapped_column(String(100), unique=True, default=None)
    facebook_token_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary, default=None)
    facebook_token_expires: Mapped[str | None] = mapped_column(String(30), default=None)

    source: Mapped[str] = mapped_column(String(30), default=PersonSource.manual.value)
    created_by: Mapped[str | None] = mapped_column(String(36), default=None)

    __table_args__ = (
        Index("idx_persons_google_sub", "google_sub", unique=True, sqlite_where=text("google_sub IS NOT NULL")),
        Index("idx_persons_facebook_id", "facebook_id", unique=True, sqlite_where=text("facebook_id IS NOT NULL")),
        Index("idx_persons_country_code", "residence_country_code"),
        Index("idx_persons_is_root", "is_root", sqlite_where=text("is_root = 1")),
        Index("idx_persons_contact_email_hash", "contact_email_hash"),
    )

    @property
    def languages(self) -> list[str]:
        if self._languages:
            return json.loads(self._languages)
        return []

    @languages.setter
    def languages(self, value: list[str]) -> None:
        self._languages = json.dumps(value)

    @property
    def alternate_nicknames(self) -> list[str]:
        if self._alternate_nicknames:
            return json.loads(self._alternate_nicknames)
        return []

    @alternate_nicknames.setter
    def alternate_nicknames(self, value: list[str]) -> None:
        self._alternate_nicknames = json.dumps(value)

    @property
    def contact_addresses(self) -> list[dict]:
        if self._contact_addresses:
            return json.loads(self._contact_addresses)
        return []

    @contact_addresses.setter
    def contact_addresses(self, value: list[dict]) -> None:
        self._contact_addresses = json.dumps(value)

    @property
    def education(self) -> list[dict]:
        if self._education:
            return json.loads(self._education)
        return []

    @education.setter
    def education(self, value: list[dict]) -> None:
        self._education = json.dumps(value)

    @property
    def career(self) -> list[dict]:
        if self._career:
            return json.loads(self._career)
        return []

    @career.setter
    def career(self, value: list[dict]) -> None:
        self._career = json.dumps(value)

    @property
    def organizations(self) -> list[dict]:
        if self._organizations:
            return json.loads(self._organizations)
        return []

    @organizations.setter
    def organizations(self, value: list[dict]) -> None:
        self._organizations = json.dumps(value)

    @property
    def admixture(self) -> list[dict]:
        if self._admixture:
            return json.loads(self._admixture)
        return []

    @admixture.setter
    def admixture(self, value: list[dict]) -> None:
        self._admixture = json.dumps(value)

    @property
    def medical_conditions(self) -> list[dict]:
        if self._medical_conditions:
            return json.loads(self._medical_conditions)
        return []

    @medical_conditions.setter
    def medical_conditions(self, value: list[dict]) -> None:
        self._medical_conditions = json.dumps(value)

    @property
    def contact_phones(self) -> list[dict]:
        if self._contact_phones:
            return json.loads(self._contact_phones)
        return []

    @contact_phones.setter
    def contact_phones(self, value: list[dict]) -> None:
        self._contact_phones = json.dumps(value)

    @property
    def contact_emails(self) -> list[dict]:
        if self._contact_emails:
            return json.loads(self._contact_emails)
        return []

    @contact_emails.setter
    def contact_emails(self, value: list[dict]) -> None:
        self._contact_emails = json.dumps(value)

    @property
    def social_accounts(self) -> list[dict]:
        if self._social_accounts:
            return json.loads(self._social_accounts)
        return []

    @social_accounts.setter
    def social_accounts(self, value: list[dict]) -> None:
        self._social_accounts = json.dumps(value)

    @property
    def name_history(self) -> list[dict]:
        if self._name_history:
            return json.loads(self._name_history)
        return []

    @name_history.setter
    def name_history(self, value: list[dict]) -> None:
        self._name_history = json.dumps(value)

    @property
    def place_history(self) -> list[dict]:
        if self._place_history:
            return json.loads(self._place_history)
        return []

    @place_history.setter
    def place_history(self, value: list[dict]) -> None:
        self._place_history = json.dumps(value)

    @property
    def display_name(self) -> str:
        if self.is_root:
            return "Our Family"
        if self.name_display_order == NameDisplayOrder.eastern.value:
            return f"{self.last_name} {self.first_name}"
        if self.name_display_order == NameDisplayOrder.patronymic.value and self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic}"
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Person id={self.id[:8]} name={self.display_name!r}>"

    @validates("contact_email")
    def _validate_contact_email(self, key: str, value: str | None) -> str | None:
        normalized = normalize_email_for_lookup(value)
        self.contact_email_hash = contact_email_lookup_hash(normalized)
        return normalized

    @validates("role")
    def _validate_role(self, key: str, value: str | None) -> str:
        normalized = (value or "").strip().lower()
        valid = {role.value for role in PersonRole}
        if normalized not in valid:
            normalized = PersonRole.admin.value if self.is_admin else PersonRole.member.value
        if normalized in {PersonRole.owner.value, PersonRole.admin.value}:
            self.is_admin = True
        elif normalized == PersonRole.steward.value:
            self.is_admin = False
        return normalized

    @validates("contact_visibility")
    def _validate_contact_visibility(self, key: str, value: str | None) -> str:
        normalized = (value or "").strip().lower()
        valid = {policy.value for policy in ContactVisibility}
        return normalized if normalized in valid else ContactVisibility.close_family.value

    @validates("sensitive_visibility")
    def _validate_sensitive_visibility(self, key: str, value: str | None) -> str:
        normalized = (value or "").strip().lower()
        valid = {policy.value for policy in SensitiveVisibility}
        return normalized if normalized in valid else SensitiveVisibility.staff.value
