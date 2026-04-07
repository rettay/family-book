import enum

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, generate_uuid, utcnow
from datetime import datetime


class AuthMethod(str, enum.Enum):
    google_oauth = "google_oauth"
    facebook_oauth = "facebook_oauth"
    magic_link = "magic_link"
    invite_code = "invite_code"
    passkey = "passkey"


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    person_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="CASCADE")
    )
    token_hash: Mapped[str] = mapped_column(String(64))  # SHA-256 of session token
    auth_method: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    expires_at: Mapped[datetime] = mapped_column()
    last_used: Mapped[datetime] = mapped_column(default=utcnow)
    ip_address: Mapped[str | None] = mapped_column(String(45), default=None)
    user_agent: Mapped[str | None] = mapped_column(String(500), default=None)

    __table_args__ = (
        Index("idx_sessions_person_id", "person_id"),
        Index("idx_sessions_token_hash", "token_hash"),
    )

    def __repr__(self) -> str:
        return f"<UserSession person={self.person_id[:8]}>"


class Invite(Base):
    __tablename__ = "invites"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    person_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="CASCADE")
    )
    token: Mapped[str] = mapped_column(String(64), unique=True)  # SHA-256 of invite token
    created_by: Mapped[str] = mapped_column(String(36))
    claimed_at: Mapped[datetime | None] = mapped_column(default=None)
    expires_at: Mapped[datetime] = mapped_column()
    revoked: Mapped[bool] = mapped_column(default=False)
    delivery_status: Mapped[str | None] = mapped_column(String(20), default=None)
    delivery_error: Mapped[str | None] = mapped_column(String(500), default=None)
    delivery_message_id: Mapped[str | None] = mapped_column(String(200), default=None)
    sent_at: Mapped[str | None] = mapped_column(String(40), default=None)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    def __repr__(self) -> str:
        return f"<Invite person={self.person_id[:8]} claimed={self.claimed_at is not None}>"


class MagicLinkToken(Base):
    __tablename__ = "magic_link_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    person_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="CASCADE")
    )
    token_hash: Mapped[str] = mapped_column(String(64))  # SHA-256
    expires_at: Mapped[datetime] = mapped_column()
    used_at: Mapped[datetime | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class PasskeyCredential(Base):
    __tablename__ = "passkey_credentials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    person_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="CASCADE")
    )
    credential_id: Mapped[str] = mapped_column(String(500), unique=True)
    public_key: Mapped[str] = mapped_column(Text)
    sign_count: Mapped[int] = mapped_column(Integer, default=0)
    label: Mapped[str] = mapped_column(String(120), default="Passkey")
    transports: Mapped[str | None] = mapped_column(Text, default=None)
    device_type: Mapped[str | None] = mapped_column(String(40), default=None)
    backed_up: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    last_used_at: Mapped[datetime | None] = mapped_column(default=None)

    __table_args__ = (
        Index("idx_passkey_credentials_person_id", "person_id"),
        Index("idx_passkey_credentials_credential_id", "credential_id"),
    )


class PasskeyChallenge(Base):
    __tablename__ = "passkey_challenges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    person_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="CASCADE"), nullable=True
    )
    challenge: Mapped[str] = mapped_column(String(200))
    ceremony: Mapped[str] = mapped_column(String(20))
    expires_at: Mapped[datetime] = mapped_column()
    used_at: Mapped[datetime | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    __table_args__ = (
        Index("idx_passkey_challenges_person_id", "person_id"),
        Index("idx_passkey_challenges_ceremony", "ceremony"),
    )
