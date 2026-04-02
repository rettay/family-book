"""SavedRecord model — external genealogy records saved to a person."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, generate_uuid


class SavedRecord(Base):
    __tablename__ = "saved_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    person_id: Mapped[str] = mapped_column(
        String, ForeignKey("persons.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str | None] = mapped_column(String(2000), default=None)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    snippet: Mapped[str | None] = mapped_column(Text, default=None)
    date_found: Mapped[str | None] = mapped_column(String(20), default=None)
    saved_by: Mapped[str] = mapped_column(
        String, ForeignKey("persons.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
