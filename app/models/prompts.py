import enum

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, generate_uuid, utcnow
from datetime import datetime


class PromptCampaignStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    closed = "closed"


class PromptResponseKind(str, enum.Enum):
    story = "story"
    media = "media"


class PromptRecipientStatus(str, enum.Enum):
    pending = "pending"
    responded = "responded"
    skipped = "skipped"


class PromptCampaign(Base, TimestampMixin):
    __tablename__ = "prompt_campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="CASCADE")
    )
    target_person_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="SET NULL"), default=None
    )
    title: Mapped[str] = mapped_column(String(300))
    prompt_body: Mapped[str] = mapped_column(Text)
    response_kind: Mapped[str] = mapped_column(
        String(20), default=PromptResponseKind.story.value
    )
    status: Mapped[str] = mapped_column(String(20), default=PromptCampaignStatus.sent.value)
    due_date: Mapped[str | None] = mapped_column(String(10), default=None)
    sent_at: Mapped[datetime] = mapped_column(default=utcnow)


class PromptCampaignRecipient(Base):
    __tablename__ = "prompt_campaign_recipients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    campaign_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("prompt_campaigns.id", ondelete="CASCADE")
    )
    recipient_person_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="CASCADE")
    )
    status: Mapped[str] = mapped_column(String(20), default=PromptRecipientStatus.pending.value)
    response_story_id: Mapped[str | None] = mapped_column(String(36), default=None)
    response_inbox_item_id: Mapped[str | None] = mapped_column(String(36), default=None)
    response_excerpt: Mapped[str | None] = mapped_column(Text, default=None)
    responded_at: Mapped[datetime | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    __table_args__ = (
        UniqueConstraint(
            "campaign_id",
            "recipient_person_id",
            name="uq_prompt_campaign_recipient",
        ),
    )
