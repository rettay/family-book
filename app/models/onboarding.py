import json

from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, generate_uuid, utcnow


class OnboardingStatus:
    active = "active"
    completed = "completed"
    skipped = "skipped"


class OnboardingProgress(Base):
    __tablename__ = "onboarding_progress"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    person_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="CASCADE"), unique=True
    )
    status: Mapped[str] = mapped_column(String(20), default=OnboardingStatus.active)
    selected_path: Mapped[str | None] = mapped_column(String(20), default=None)
    _milestones: Mapped[str | None] = mapped_column("milestones", Text, default="{}")
    started_at: Mapped[datetime] = mapped_column(default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(default=None)
    skipped_at: Mapped[datetime | None] = mapped_column(default=None)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    @property
    def milestones(self) -> dict:
        return json.loads(self._milestones) if self._milestones else {}

    @milestones.setter
    def milestones(self, value: dict) -> None:
        self._milestones = json.dumps(value)
