import json

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, generate_uuid, utcnow
from datetime import datetime


class BookProject(Base, TimestampMixin):
    __tablename__ = "book_projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(300))
    subtitle: Mapped[str | None] = mapped_column(String(300), default=None)
    introduction: Mapped[str | None] = mapped_column(Text, default=None)
    _person_ids: Mapped[str | None] = mapped_column("person_ids", Text, default="[]")
    _story_ids: Mapped[str | None] = mapped_column("story_ids", Text, default="[]")
    _media_ids: Mapped[str | None] = mapped_column("media_ids", Text, default="[]")
    include_timeline: Mapped[bool] = mapped_column(Boolean, default=True)
    markdown_path: Mapped[str | None] = mapped_column(String(500), default=None)
    pdf_path: Mapped[str | None] = mapped_column(String(500), default=None)
    generated_at: Mapped[datetime | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    @property
    def person_ids(self) -> list[str]:
        return json.loads(self._person_ids or "[]")

    @person_ids.setter
    def person_ids(self, value: list[str]) -> None:
        self._person_ids = json.dumps(value)

    @property
    def story_ids(self) -> list[str]:
        return json.loads(self._story_ids or "[]")

    @story_ids.setter
    def story_ids(self, value: list[str]) -> None:
        self._story_ids = json.dumps(value)

    @property
    def media_ids(self) -> list[str]:
        return json.loads(self._media_ids or "[]")

    @media_ids.setter
    def media_ids(self, value: list[str]) -> None:
        self._media_ids = json.dumps(value)
