"""Story model — attributed, wiki-style narratives attached to a person."""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, generate_uuid


class Story(Base, TimestampMixin):
    __tablename__ = "stories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    person_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("persons.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    author_person_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("persons.id"), nullable=False
    )
    # Reserved for future voice attachment — not wired to any UI this sprint
    audio_media_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("media.id"), nullable=True, default=None
    )
    source: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    def __repr__(self) -> str:
        return f"<Story {self.id[:8]} person={self.person_id[:8]}>"
